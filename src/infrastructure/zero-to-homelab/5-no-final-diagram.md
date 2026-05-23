---
layout: article
title: "No Final Diagram"
created: 2026-05-23
category: homelab
keywords: homelab, architecture evolution, Docker, infrastructure lifecycle, operational sustainability
excerpt: Every stage of this homelab simplified something the previous stage made too complex. The next one will do the same. Infrastructure does not converge on a final state. It converges on a clearer understanding of what you actually need.
permalink: /homelab/no-final-diagram/
series: From Zero to Homelab
series_episode: 5
---

## The pattern in retrospect

The original plan had four nodes. A network node, a compute node, a storage node, a backup node. Each with a clear role, each justified by a separation of concerns that looked right on paper.

Power consumption killed the four-node design. The compute node was absorbed into the storage node. The backup node became a virtual machine. The architecture contracted from four physical machines to two, and the homelab became something I could actually afford to run continuously.

That was [Episode 2](/homelab/compute-architecture/). At the time, it felt like the architecture had found its shape. Two nodes, clear role separation, sustainable power draw. The design was clean.

It was also, I now realise, the beginning of the next simplification.

---

## What the current architecture got right

The network node works. OPNsense, the reverse proxy, the SSO layer, the network controller: all of it runs on a low-power machine that does one thing well and does not need attention. The segmentation model, the default-deny policy between VLANs, the WireGuard layers: none of this needs to change. It was designed conservatively, and conservative designs age well.

The GitOps pipeline works. A private repository as single source of truth, encrypted secrets, a convergent deploy process. The philosophy of treating every change as a commit is not tied to the current tooling. It is a principle that survives any implementation change.

The backup strategy works. PBS for the virtualisation layer, Borg for application-level datasets, offsite replication, automated verification. [Episode 4](/homelab/backup-and-monitoring/) covered why this matters. The strategy adapts to whatever runs underneath it.

What does not work as well is the layer between these things and the services they support.

---

## Where the friction lives

The storage node runs Proxmox. Proxmox manages LXC containers. Each LXC container runs Docker Compose stacks. The services live inside Docker, but Docker lives inside LXC, and LXC lives inside a hypervisor that was designed for a multi-node cluster.

Proxmox is not the wrong tool. Its snapshot management, backup integration, storage handling, and console access remain valuable even on a single node. But when the homelab had ambitions of live migration, high availability, and distributed workloads, the full hypervisor abstraction made sense as the default for everything. In practice, the cluster is two nodes. Live migration is possible but rarely used. High availability was never fully implemented. Proxmox remains useful, but it is no longer the right default abstraction for workloads that are fundamentally Docker Compose stacks.

Meanwhile, the LXC layer adds overhead without adding proportional value. The containers exist to group services and isolate network segments, but Docker's own network model can handle part of the grouping and service-level isolation that I was previously delegating to LXC. It does not replace every form of isolation, particularly not VLAN segmentation or inter-segment policy, which remain the network node's responsibility. But within the workload host, the LXC boundary is solving a problem that Docker networks and host-level configuration can address with less machinery.

The friction is tangible. Every LXC container needs its own Docker installation, its own deploy tooling, its own update cycle. Debugging a connectivity issue means tracing through Docker bridge networks, LXC network interfaces, and VLAN tagging on the hypervisor. Deploying the same change across multiple containers means repeating the same operation in each one. The grouping is useful, but the mechanism is heavier than it needs to be.

The monitoring problem described in [Episode 4](/homelab/backup-and-monitoring/) is a symptom of this. More containers means more things to watch. More layers means more places where something can break without being visible. The instinct to add observability tools is a response to complexity that should not have been there in the first place.

---

## The direction, not the destination

The next stage simplifies the workload host. Docker runs natively on the operating system, not inside LXC containers managed by a hypervisor. Compose stacks are deployed directly. The virtualisation layer remains available for the few workloads that genuinely require it, but it is no longer the default abstraction for everything.

This is not simplification without security consequences. It is a trade that makes security more explicit and, for this environment, more manageable. Centralising Docker on a single host means one hardening baseline to maintain: one set of socket permissions, one firewall configuration, one update policy, one place where a Docker socket proxy can restrict access when services need it. Distributing the same workloads across multiple LXC containers means repeating that hardening in each one, with each repetition being a surface where something can be misconfigured. Fewer hosts, fewer boundaries to maintain, fewer places to make mistakes.

The network node stays exactly as it is. It was the most conservative design in the homelab, and that conservatism is paying off now. The workload architecture changes; the network architecture does not.

The backup strategy adapts rather than changes. PBS remains relevant for any virtualised workloads that survive the transition, while application-level recovery increasingly depends on Borg, declarative Compose files, and tested restore paths. The principle from [Episode 4](/homelab/backup-and-monitoring/) holds: what matters is that every dataset has a verified, restorable copy offsite.

The specifics of the implementation are still open. The operating system is an implementation detail: it may be a minimal Linux host, or Proxmox used in a more restrained, Docker-native way. The GitOps pipeline will follow the same philosophy, though the tooling may change if a container management platform handles deployment more cleanly than custom scripts. These are implementation choices, not architectural ones. The principle remains: every service is declared in code, every change is versioned, every secret is encrypted at rest.

I am not going to describe the final architecture in this episode, because it does not exist yet. What exists is the reasoning that produces it, and that reasoning has been consistent across every stage of this homelab. The next design will be judged by fewer moving parts, fewer privileged boundaries to maintain, clearer restore paths, and less operational ceremony for ordinary service updates.

---

## What each stage actually taught

[Episode 0](/homelab/why-homelab-matters/) was about understanding why you build infrastructure at all. The answer was not independence for its own sake. It was the operational visibility that comes from being responsible for every layer of the stack.

[Episode 1](/homelab/home-network-design/) was about designing a network you can reason about. The lesson was that you understand systems by breaking them, and that a residential network can be segmented and governed like a professional one if you are willing to accept the complexity.

[Episode 2](/homelab/compute-architecture/) was about constraints. Power, noise, maintenance burden. The lesson was that good architecture is what survives contact with real operating costs, not what looks cleanest in the first diagram.

[Episode 3](/homelab/gitops-and-secrets/) was about control. If you cannot reproduce your infrastructure from a repository, you do not control it. You are merely running it.

[Episode 4](/homelab/backup-and-monitoring/) was about trust. Backup and monitoring are the proof that your infrastructure takes its own continuity seriously. Without them, everything else is provisional.

This episode is about the recognition that none of these lessons point to a final state. Each one produces an architecture that is better than the last, which also means each one eventually reveals the friction that the next stage will resolve.

---

## Why a homelab is never finished

There is a version of this series that ends with a diagram. A clean, labelled architecture with every component in its place, every connection justified, every design decision resolved. The kind of diagram you might put in a portfolio or a conference slide.

That diagram does not exist, and it never will.

A homelab is not a project with a deliverable. It is a practice. The point is not to redesign endlessly. The point is to recognise when an abstraction that once solved a real problem has become a source of operational drag. The infrastructure changes because the person operating it changes. You learn what you actually need by running what you thought you needed and discovering where it falls short. The four-node design was not wrong. It was the design of someone who had not yet paid a real electricity bill for running four machines continuously. The two-node design was not wrong either. It was the design of someone who had not yet felt the friction of managing a hypervisor cluster for workloads that do not need one.

But there is a constraint more fundamental than power draw or architectural elegance. A homelab is a hobby. It simplifies my life with sovereign, self-hosted services and a level of data protection that no third-party provider can match. It teaches me things that directly inform my professional work, through genuine learning by doing rather than theoretical study. It gives back more than it takes. But it remains something I do alongside everything else, not instead of everything else. The commitment it demands must stay within the bounds of what I can realistically sustain, not what I choose to give during a burst of enthusiasm on a free weekend. When the infrastructure requires more ongoing attention than the person operating it can provide, the architecture is the problem, not the person.

The next design will not be wrong. It will be the best answer I have today, shaped by everything the previous stages taught me. And at some point, it too will reveal the constraint I cannot see yet.

That is not a flaw in the process. That is the process.
