---
layout: article
title: "What Breaks, What Survives"
created: 2026-05-23
category: homelab
keywords: backup, monitoring, Proxmox Backup Server, Borg, 3-2-1, observability, disaster recovery
excerpt: Backup and monitoring are not separate concerns. Monitoring tells you when something breaks; backup determines how far back you can go. Together, they form the operational contract that makes the rest of the infrastructure sustainable.
permalink: /homelab/backup-and-monitoring/
series: From Zero to Homelab
series_episode: 4
---

## The migration that proved the strategy

When I moved from the single OpenMediaVault server to the Proxmox architecture, the old server did not stay online as a fallback. The hardware was the same. I wiped the operating system, reinstalled, and started building the new infrastructure on the same machine. By the time Proxmox was running, the previous system no longer existed. What remained were the storage drives and the backups.

Every service configuration, every database, every user file had to come back from one of those two sources. There was no parallel operation, no rollback path to a working system. The backups were either complete and restorable, or the migration meant starting from scratch.

They were complete and restorable.

I rebuilt every service from backup, recovered application data and configurations without loss, and brought the infrastructure back online on a fundamentally different platform. The system changed entirely. The data survived intact.

That migration was the moment backup stopped being a configuration task and became something I trusted. Not because I had decided to trust it, but because it had delivered under the only conditions that matter: the ones where there is no alternative.

---

## The logic behind the layers

The backup architecture follows a 3-2-1 strategy. At least three copies of any dataset. On at least two different media. With at least one offsite.

This is not an aspirational framework. It is the minimum that makes recovery plausible across the range of failures that actually occur: a corrupted filesystem, a misconfigured update, a hardware failure, or a scenario where the entire local infrastructure is unavailable.

The implementation uses two systems. Proxmox Backup Server handles the virtualisation layer. Borg handles application-level datasets that require their own backup logic. Both are deduplicated, both are encrypted before leaving the infrastructure, and both follow the same retention policy for offsite copies.

---

## Proxmox Backup Server and the virtualisation layer

PBS runs as a virtual machine on the storage node, with its data sitting in a dedicated ZFS dataset with constrained quotas. It backs up every virtual machine and every LXC container in the cluster, with one exception that deserves its own section.

Local backups retain the last two snapshots. This is not the recovery archive. It is the fast-access layer, the one that covers the most common scenario: something broke in the last change, and I need to roll back quickly.

The offsite layer is where the real retention lives. PBS replicates to S3-compatible object storage on a 25-hour cycle, maintaining seven daily, four weekly, twelve monthly, and two yearly snapshots. The 25-hour interval means the push window drifts naturally across the day rather than always competing with the same workloads at the same hour.

Backups are deduplicated and encrypted before leaving the infrastructure. PBS uses client-side encryption, with the backup server never receiving the decryption material. The storage provider sees only opaque, deduplicated blocks. This is not a theoretical concern. When your offsite backups live on someone else's infrastructure, the encryption model is the boundary between delegation and exposure.

PBS also handles its own housekeeping. Garbage collection reclaims space from expired snapshots. Verification jobs run periodically against both local and remote stores, checking that every backup can be read back and that no silent corruption has crept in. Verification tells me that the backup data is readable. Periodic restore tests tell me that the recovery procedure itself still works. The distinction matters: the backup that exists but cannot be restored is worse than no backup at all, because it gives you false confidence.

---

## The exception that proves the architecture

OPNsense cannot be backed up like everything else.

A full snapshot of the firewall virtual machine would require freezing its state, which means freezing the network. Every service that depends on routing, DNS, or firewall rules would pause. For a system that is the single point of network availability, this is not an acceptable trade-off.

The lesson was immediate and went beyond backup. The firewall is the service you need running to reach your offsite storage, and it is also the service you cannot freeze without losing access to everything else. You cannot back up to the cloud the device you need to reach the cloud. This is what a homelab is for: making operational dependencies visible in a way that no diagram or documentation ever does.

The solution was a dedicated strategy. OPNsense exports its configuration, and that configuration is sent via SSH to a storage box offsite. The configuration file is small, changes infrequently, and contains everything needed to rebuild the firewall from a clean installation. If the VM is lost, the recovery path is a fresh OPNsense install and a configuration import, not a full image restore.

There is an architectural alternative I evaluated and deferred. Running OPNsense in high availability, with two firewall VMs on separate nodes, would allow one instance to maintain the network while the other is being snapshot. But HA for the firewall requires a dedicated switch for the WAN segment, hardware I have not yet acquired and a configuration path I have not yet explored. It remains a future option, not a current one. For now, the config-only backup covers the actual recovery need without adding complexity that the rest of the architecture is not ready to support.

This is worth stating explicitly: not every component benefits from the same backup strategy. The firewall needs configuration backup, not state backup. Recognising the difference avoids both unnecessary risk and unnecessary complexity.

---

## Application-level backups with Borg

Some services manage data that does not live cleanly inside the container filesystem. The photo library and the file cloud both have databases, metadata, and large binary datasets that benefit from application-aware backup rather than block-level snapshots.

These services use Borg repositories stored on a dedicated storage box offsite. The retention policy mirrors the one used for PBS: seven daily, four weekly, twelve monthly, two yearly. Borg follows the same principle at the application layer: the remote repository stores only encrypted, deduplicated data, while the key material remains under my control.

The file cloud handles its own backup internally through its built-in tooling, which ensures database consistency before the export runs. The photo library and media services take a different approach. The container that hosts them runs a pre-backup hook that triggers the Borg job before PBS snapshots the container itself. This means the Borg backup of application data completes first, and then the container-level backup captures the state after the application backup has finished. The two layers are sequenced, not competing.

This is not elegance for its own sake. It is a response to a real problem: backing up a database by snapshotting the filesystem underneath it can produce a backup that is internally inconsistent. Application-aware backup avoids this by letting the application prepare its own state before the snapshot runs.

---

## Knowing when something breaks

Backup answers the question of how far back you can go. Monitoring answers the question of when you need to.

The monitoring stack is, at this stage, a minimum viable layer. Proxmox and PBS both provide built-in notification systems that report on backup job outcomes, verification results, and storage health. These generate email alerts when something fails or when a verification job detects inconsistencies. If a backup does not complete, I know about it. If a completed backup fails verification, I know about that too.

For service-level observability, Uptime Kuma monitors every running service, including those that are only exposed internally. It checks availability at regular intervals and sends email alerts when a service has been unreachable for a sustained period. The threshold is set high enough to avoid noise from routine restarts and low enough to catch real outages before I discover them by accident.

This is the baseline, not the end state. I evaluated more elaborate approaches, from metrics platforms with collection agents to AI-assisted tools that could correlate events across services. Each would improve visibility. Each also adds operational surface area and, in some cases, privilege levels that made me uncomfortable. A monitoring agent with broad read access across the entire infrastructure is a powerful diagnostic tool. It is also a component that itself needs securing, updating, and trusting.

The current approach handles the two questions that matter most: is everything running, and are the backups healthy. But the gap between this baseline and the more comprehensive observability I would like is one of the forces pulling toward a simpler architecture. Fewer containers, fewer moving parts, fewer things to monitor. The monitoring problem and the architecture problem are not separate. They are the same problem seen from different angles.

---

## The contract between the two

Backup and monitoring are often treated as separate chapters in infrastructure guides. In practice, they are two halves of the same operational commitment.

Monitoring without backup tells you something is wrong but gives you no way to recover. Backup without monitoring gives you recovery points but no way to know whether they are still valid or whether something broke days ago. Together, they form the minimum viable contract between you and your infrastructure: I will know when something fails, and I will be able to go back to a state before it failed.

The series so far has covered how the network is designed, how compute is structured, how changes are deployed. None of those layers is useful if you cannot recover from the moment they stop working. This episode is not about a feature of the homelab. It is about the condition that makes all the other features trustworthy.

---

## What I would not do again

Trusting that a successful backup job means a restorable backup. Early on, I relied on job completion status as proof that offsite backups were healthy. I did not verify that the remote data could actually be read back and restored. PBS now runs verification automatically against both local and remote stores, but the gap between "the job completed" and "the backup is restorable" is exactly the gap where false confidence lives.

Adding monitoring complexity before simplifying the thing being monitored. The instinct is to add observability layers to understand a system that feels opaque. The better instinct, which took longer to develop, is to ask whether the system itself is more complex than it needs to be. A simpler architecture does not need less monitoring because it is less important. It needs less monitoring because there is less to go wrong.

---

## What backup and monitoring taught me

Every system in this homelab exists because I built it, and every failure is mine to resolve. Backup and monitoring are where that responsibility becomes concrete.

They are not features you add after the architecture is complete. They are the architecture's proof of seriousness. An infrastructure that cannot tell you when it is broken and cannot recover when it does is not infrastructure. It is a project that has not yet been tested by its first real failure.
