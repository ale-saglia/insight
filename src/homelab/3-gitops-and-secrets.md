---
layout: article
title: The Commit Is the Deploy
created: 2026-04-18
modified: 2026-04-18
category: homelab
keywords: GitOps, SOPS, AGE, infrastructure as code, Docker Compose, Renovate, homelab automation
excerpt: How a private Git repository, a deploy script, and encrypted secrets turned a multi-node homelab into infrastructure that scales without scaling complexity.
permalink: /homelab/gitops-and-secrets/
series: From Zero to Homelab
series_episode: 3
---

## The problem with doing things properly

[Episode 2](/homelab/compute-architecture/) ended with a two-node Proxmox cluster running several LXC containers, each hosting Docker Compose stacks. The architecture was deliberately segmented: separate containers for network services, media, personal tools, secrets management. Better isolation, clearer boundaries, smaller blast radius.

But segmentation has an operational cost.

Adding a service meant opening an SSH session to the right container, creating the Compose file, writing the environment variables, copying secrets from wherever they were last stored, running the stack, and hoping the configuration matched what was running on the other hosts. Updating a service meant doing this again. Updating across multiple hosts meant doing it several times and keeping track mentally. Rolling back meant remembering what the previous state was.

At some point, I realized the architecture I had built to reduce risk was introducing a different kind of risk: the risk of not changing things because changing them was tedious. Services stopped getting updated. New ideas stayed in a note file instead of being deployed. The infrastructure was sound but operationally stale.

The previous setup, a single server running OpenMediaVault with Watchtower, had the opposite problem. Updates happened automatically with no review, no versioning, and no rollback path. That works until it does not. With multiple hosts, uncoordinated blind updates would have been worse: the same unreviewed change happening independently on different machines, with no record of what changed.

The question was not whether to automate. It was how to automate in a way that remains legible, auditable, and reversible.

---

## The repository as source of truth

The entire service layer is defined in a single private repository. Every Docker Compose file, every environment variable, every encrypted secret, every host-to-stack mapping lives in version control. The repository is not a mirror of what is running. It is the definition of what should be running.

The structure separates what runs where from how it is configured. The repository has three main areas: `host/` declares which stacks run on each host via a `stacks.yaml` file, `stacks/` contains the actual Compose definitions and encrypted secrets for each service, and `global/` holds shared configuration. The full flow from commit to running containers looks like this:

![GitOps deploy pipeline](/assets/homelab-gitops-pipeline.svg)

Each host has a `stacks.yaml` that is just a list of stack names. Nothing else. The actual stack definitions, Compose files, environment variables, and SOPS-encrypted secrets, live under `stacks/`, organized by service name.

Adding a service to a host is a one-line change in `stacks.yaml`. Moving a service between hosts is two one-line changes. The stack definition itself does not know or care which host runs it.

The repository is hosted on GitHub but mirrored to a local Gitea instance. Deploys pull from the local mirror when available, so they do not depend on a single external service being reachable.

---

## How a deploy happens

A systemd timer on each host runs the deploy script every five minutes. The deploy loop is timer-based rather than event-driven. For this setup, the simplicity and failure isolation of polling outweighed the benefits of a push-based model: no webhook endpoint to expose, no CI/CD pipeline to maintain, no message broker to run. If a cycle fails, the next one retries from clean state.

The script does four things in sequence.

**Pull.** It fetches the latest state from the remote repository. The remote is the source of truth. Local changes are discarded via hard reset. This is deliberate: if something was modified directly on a host, it was either a temporary fix that should have been committed, or a mistake that should not persist.

**Decrypt.** It checks which secret files have changed since the last pull. If any `*.secret.env` file was modified, or if a decrypted copy is missing, it decrypts only the affected files. The decryption runs SOPS inside a pinned, digest-verified container image, using an AGE private key that lives on the host and is never committed. The decrypted files are written with mode 600 and excluded from version control.

**Teardown.** If a stack was removed from a host's `stacks.yaml` since the last deploy, the script detects the orphaned containers and brings them down. This works in two passes: first by comparing running Compose projects against the declared list, then by scanning Docker labels to catch containers that Compose parsing might miss, such as stacks whose directory was deleted or whose environment files are no longer resolvable.

**Converge.** It iterates over the stacks declared for that host, loads the relevant environment files and decrypted secrets, pulls the latest images, and runs `docker compose up -d`. If nothing changed, Docker sees the same configuration and does nothing.

The result is convergent. The system continuously aligns itself to the state defined in the repository. A commit is, within five minutes, a deploy.

This is not a full GitOps controller in the Kubernetes sense. There is no declarative reconciler, no admission webhook, no per-container state comparison. But there is a basic form of drift enforcement: the teardown pass removes any running container that is not declared in the host's `stacks.yaml`. If something was started manually or left behind from a previous configuration, it gets cleaned up within five minutes. It is a simpler pull-based convergence loop that applies the same core idea, Git as the source of truth, without introducing an additional control plane. For the scale of this infrastructure, a deploy script and a timer are the right tool. The complexity is in the workflow, not in the tooling.

---

## Encrypted secrets in the repository

The first objection to storing infrastructure in Git is usually about secrets. API keys, database passwords, SMTP credentials. They cannot go into a repository in plaintext, even a private one.

SOPS solves this. Every file matching `*.secret.env` is encrypted with AGE before being committed. The encryption is AES-256-GCM. The AGE public key is in the repository's `.sops.yaml` configuration. The private key stays on each host, in a protected directory under root, and is provisioned once during bootstrap.

What this means in practice: the repository contains files like `authentik.secret.env` that are fully encrypted. When the deploy script runs, it decrypts them into `.decrypted.authentik.secret.env`, which Docker Compose then reads as environment variables. The decrypted files are gitignored and never leave the host.

Day to day, I edit secrets from my laptop, which has an encrypted disk and a VSCode plugin that handles SOPS decryption and re-encryption transparently. Open the file, edit the value, save. The plugin re-encrypts on save. The commit contains only ciphertext. If I ever need to edit secrets from a different machine, the fallback is minimal: any computer with Git, SOPS, and AGE installed is enough. The AGE private key is stored in my password manager, so the recovery path does not depend on a single device.

This workflow has a deliberate trade-off: secrets cannot be edited from a phone or a web browser. For a homelab, this is an acceptable constraint. It is also, arguably, a feature. The inability to modify secrets from an arbitrary device is a security boundary, not a limitation.

The security model is convenience-aware, not convenience-optimized. Compromising a host would expose its AGE key and the decrypted secrets for its local stacks. It would not automatically grant access to all data: services are isolated at the container and network level, and hosts are not directly reachable from outside the network. There is no SSH access enabled by default; the firewall blocks it unless a temporary rule is explicitly created. This is still a significant improvement over the previous setup, where secrets lived in plaintext files on each host, manually copied and occasionally forgotten.

---

## Updates as pull requests

Images in the Compose files are not tagged with `latest` or `alpine`. Every image reference includes a static version tag and a SHA256 digest. This means the image that runs is always the exact image that was committed. If an upstream registry is compromised or a tag is reassigned, the digest mismatch prevents the wrong image from being pulled. Mutable tags assume that upstream registries are always trustworthy. Recent supply-chain incidents suggest otherwise.

Keeping those digests current is [Renovate](https://github.com/renovatebot/renovate)'s job. Renovate scans the Compose files weekly, detects available updates, and opens a pull request with the new tag and digest already applied. The PR is reviewed, and once merged, the next deploy cycle picks it up.

Not all updates are treated equally. Services that do not handle sensitive data and whose compromise would not expose other parts of the infrastructure allow digest-only updates to auto-merge: same tag, rebuilt image, no breaking change expected. For everything else, including any minor or major version bump, the PR requires manual review. Major PostgreSQL upgrades, for instance, trigger an explicit warning in the PR body because a major version bump is incompatible with the existing data directory without migration.

The result is that updates are deliberate, traceable, and reversible. Every image change is a commit with a clear diff. If an update breaks something, the fix is a revert. If I want to know what version of a service was running three weeks ago, I check the Git history. The PR history also serves as an implicit changelog, which matters for the backup episode: knowing exactly what was running at the time of a backup makes restores meaningful.

---

## What this changes operationally

The deploy pipeline removed an entire category of work.

Creating a new service means writing a Compose file and an environment file, encrypting any secrets, adding the stack name to a host's `stacks.yaml`, and committing. Within five minutes, the service is running. No SSH session needed.

Removing a service means deleting the stack name from `stacks.yaml` and committing. The teardown pass detects the orphaned containers and removes them.

Moving a service between hosts means editing two `stacks.yaml` files. The old host tears it down, the new host brings it up.

Rolling back a broken change means reverting the commit. The next deploy cycle restores the previous state.

All of this works from any Git client. A laptop, a tablet, a phone with a Git app. The only operation that requires something beyond a Git client is editing encrypted secrets, which needs any device with the AGE key and SOPS installed.

New LXC containers are provisioned from a common template that already includes Docker, the deploy tooling, and the SSH configuration for the pipeline. Cloning the template, assigning a VLAN, and adding a `host/` directory with a `stacks.yaml` is the entire onboarding process for a new host.

---

## What I would not do again

Relying on automated image updates with no review step. Watchtower on the old OMV server would pull whatever was newest. For a single machine running non-critical services, the blast radius was limited. For a segmented multi-host setup, uncoordinated updates across hosts with no record of what changed would have been a liability.

Using `latest` or mutable tags in Compose files. A tag that can be reassigned upstream is not a version pin. It is a hope. Digest pinning is more verbose, but it means the deploy is deterministic. What you committed is what runs.

Storing secrets outside version control entirely. Before this setup, secrets lived in files on each host, manually copied, occasionally forgotten. Encrypting them in the repository means they are versioned, backed up, and impossible to lose by accident. The trade-off is the key management overhead, but that overhead is small and one-time.

---

## What versioned infrastructure actually means

The shift from "I configured services on hosts" to "the repository defines what runs" is not primarily about automation. It is about legibility.

At any point, I can read the repository and know the complete state of the infrastructure. Which services run on which host. What version of each image is deployed. What secrets exist and when they were last changed. What was different a month ago.

The setup phase is more complex than a traditional Compose-based approach. Once in place, the day-to-day operation is simpler: changes are centralized, repeatable, and do not require direct access to hosts. The system shifts complexity from routine operations to initial design. The cost is upfront. The benefit is that routine changes become trivial.

This is the same principle that makes infrastructure as code valuable in enterprise contexts, but in a homelab, there is an additional dimension. I am the only operator. There is no team to hand off to, no documentation that someone else will read. But there is a future version of myself who will need to understand a decision made today. The commit history is that documentation.

In professional contexts, particularly in public administration, the absence of this kind of traceability is common. Systems are configured manually, updates happen through undocumented procedures, and the gap between what is supposed to be running and what is actually running grows silently. Having operated a system where every change is a commit with a timestamp, a diff, and an author has changed how I evaluate infrastructure governance. The question is no longer whether a system works. It is whether anyone can tell you why it works, and what changed last.
