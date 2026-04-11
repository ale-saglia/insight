---
layout: article
title: Why I Built a Homelab (and Why It Matters)
date: 2026-03-27
category: homelab
excerpt: Journey from commercial cloud dependency to self-sufficient infrastructure. From frustration to capability.
permalink: /homelab/why-homelab-matters/
---

## Context

My homelab journey started around 2018.

At the time, I tried to build a small NAS using a Raspberry Pi 4, two SSDs, and a UPS, mainly to run NextcloudPi. The goal was simple: reduce dependency on large tech platforms.

I had been using a terabyte of Google Drive storage — until that option was removed. The alternatives were either paying (not trivial as a student) or figuring things out myself.

I chose the second.

---

## Early failures

It did not go well.

Things would work for a while — until they did not. An update would break something. A configuration would drift. A service would silently stop responding.

My limited experience, combined with the complexity of managing a bare-metal system, meant that I rarely understood *why* things broke — only that they had. Even though I was already using Linux on desktop, operating a persistent system was a different problem entirely. A desktop you can reboot. A NAS running your only cloud storage, you cannot.

After a while, I would give up and return to some compromise with commercial services.

This cycle repeated for years:

- the desire for independence
- the frustration of becoming a sysadmin without being one

---

## The shift: Docker

Things changed between 2023 and 2024, when I discovered Docker.

Decoupling the system from the software introduced a different way of thinking. I quickly moved to Docker Compose to manage my services.

Until then, I had mostly worked with Raspberry devices and had limited experience with virtualization (aside from a previous project running on a VM).

Docker made systems:

- easier to reproduce  
- easier to debug  
- easier to reason about  

For the first time, things started to stick.

---

## From self-hosting to homelab

I never abandoned the idea of running my own services, but recently it evolved into something more structured.

After moving to a new house, I designed the network infrastructure from scratch:

- cabling (fiber and Ethernet)  
- switches  
- VLAN segmentation (8 VLANs managed via OPNsense running in a VM)  

I also moved from a single machine to a small multi-node setup using Proxmox.

Originally, I planned three nodes, but energy costs pushed me toward a two-node architecture.

The result is a more robust system, with better isolation and improved reliability.

---

## Operational maturity

More recently, I introduced a GitOps-style approach.

All services are managed via Docker and deployed through scripts connected to a GitHub repository. This allows:

- reproducible deployments  
- quick rollback  
- controlled experimentation  

Infrastructure changes are now versioned, not improvised.

---

## What a homelab actually teaches

At this point, the homelab is no longer just about independence.

It provides something difficult to replicate in enterprise environments:

- a single decision-maker across the entire stack  
- full visibility, from physical layer to application layer  
- direct exposure to maintenance costs  
- constant interaction with failure modes  

A homelab forces decisions that are often abstract elsewhere.

You are constantly dealing with:

- downtime  
- backups  
- redundancy  
- time investment  

---

## Closing

Running even a small system over time makes one thing clear:

Infrastructure is not just about building systems — it is about sustaining them.