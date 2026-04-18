---
layout: category
title: Homelab
category: homelab
permalink: /homelab/
summary: Category hub for homelab content, including the Zero to Homelab series and broader infrastructure topics.
---

This category collects homelab content by genre, including the Zero to Homelab series.

Focus: lifecycle responsibility, reliability constraints, and real-world operational trade-offs.

## Episodes

The episodes below are part of the series **Zero to Homelab**.

**[Episode 0: Why I Built a Homelab (and Why It Matters)](/homelab/why-homelab-matters/)**

Journey from commercial cloud dependency to self-sufficient infrastructure. Understanding the motivation and learning from early failures - until discovering containerization changed everything.

*Topics:* NAS setup, Docker, operational autonomy, infrastructure independence

*Lesson:* You understand infrastructure when the operational complexity is removed, not added to your learning curve.

**[Episode 1: Building a Home Network You Actually Control](/homelab/home-network-design/)**

Designing residential network infrastructure from scratch. Architectural decisions, virtualization trade-offs, and the reality of operating your first virtual firewall.

*Topics:* OPNsense, network segmentation, infrastructure design, resilience

*Lesson:* You understand systems by breaking them, then figuring out why they broke - not before.

**[Episode 2: Two Nodes, One Lesson in Constraint](/homelab/compute-architecture/)**

From a four-node plan to a two-node reality. How power, noise, operational complexity, and data-layer choices shaped the compute architecture.

*Topics:* Proxmox, LXC vs VM, energy efficiency, ZFS, NFS, service/data separation

*Lesson:* Good architecture is what remains sustainable under real operating constraints, not what looks cleanest in the first diagram.

**[Episode 3: The Commit Is the Deploy](/homelab/gitops-and-secrets/)**

How a private Git repository, a deploy script, and encrypted secrets turned a multi-node homelab into infrastructure that scales without scaling complexity. Every Compose file, variable, and secret is version-controlled. A commit is a deploy, every change is traceable and reversible, and secrets are secured with SOPS and AGE.

*Topics:* GitOps, SOPS, AGE, automation, secrets management, convergent pipeline, safe updates

*Lesson:* Infrastructure is truly under control when every change is a readable, auditable, and reversible commit.
