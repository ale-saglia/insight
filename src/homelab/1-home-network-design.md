---
layout: article
title: Building a Home Network You Actually Control
created: 2026-04-11
modified: 2026-04-11
category: homelab
keywords: home network design, network segmentation, firewall, OPNsense, network infrastructure
excerpt: Designing residential network infrastructure from scratch with architectural separation of concerns and principled infrastructure design.
permalink: /homelab/home-network-design/
series: From Zero to Homelab
series_episode: 1
---

## Starting point

When I moved to a new house, I had a choice.

I could plug in a consumer router and be done with it. Or I could treat the move as an opportunity to build a network infrastructure from scratch, properly.

I chose the second. This is what that actually involved, and what it taught me.

---

## The first decision: physical or virtual firewall

The question I faced immediately was where to run the firewall.

The obvious path was a dedicated appliance: a small x86 box running pfSense or OPNsense, separate from everything else. Simple, predictable, cheap.

I chose the other path: virtualizing the firewall inside a hypervisor, on a node dedicated exclusively to the network layer. That node now runs OPNsense, the wireless controller, and the services responsible for authentication and traffic routing. It is physically and logically separate from the compute and storage infrastructure.

This separation was not strictly necessary at the start. It became a deliberate design choice once I understood what it meant: the network layer can be reasoned about, maintained, and failed independently from everything running on top of it. This is not a novel concept in enterprise architecture. It is, however, one thing to read about it and another to operate it.

---

## pfSense or OPNsense

Both are FreeBSD-based. Both are capable. The differences that mattered were around approach.

pfSense has a longer history and a larger community. It is also, in places, visibly anchored to older decisions, in the interface and in how certain features are exposed.

OPNsense felt more deliberately designed. The API is first-class. The plugin system is clean. Updates are frequent and well-documented.

I was starting from zero. If I had to learn one, I preferred to learn the one with the more modern design language. OPNsense it was.

---

## The chicken-and-egg problem

Here is something nobody warns you about when you virtualize a firewall for the first time.

To configure OPNsense, you need network access. But OPNsense is what provides network access. If you misconfigure it, you lose the ability to reach the interface you need to fix it.

My previous router became my lifeline during setup: a parallel network I used as a fallback path to reach the hypervisor when the virtual firewall was not yet routing correctly, or was completely broken, which happened more than once.

It took longer than I expected. There were evenings where I rebuilt the virtual machine configuration from scratch because I had gotten into a state I did not understand well enough to fix. That was, in hindsight, the point. You understand a system when you have broken it and repaired it, not before.

---

## Physical infrastructure

The house was cabled during the move. The backbone between floors runs on single-mode fiber with BiDi transceivers at 10 Gbps. The choice of fiber over copper for the backbone was partly practical: fiber cables are thinner and easier to pull through existing conduits inside walls. Using BiDi modules, which transmit and receive on different wavelengths over a single fiber strand, halved the number of physical cables needed between switches.

End-device connections use copper, which is more than sufficient for anything currently attached.

The WAN connection is fixed wireless, with an antenna mounted on the roof. Living on top of a hill, with no shared lightning protection in the building, exposed me to a risk I had not initially considered. A lightning strike on the antenna could propagate through the Ethernet cable directly into the router, and from there into everything else.

The mitigation was deliberate: a copper-to-fiber media converter sits between the antenna's injector and the router. The signal enters as light, not electricity. A surge on the antenna side cannot travel down an optical path. The injector itself is on a UPS, as are the servers and all active network equipment, providing continuity for a minimum viable setup during power interruptions.

---

## Why segmentation

My previous self-hosting experience had taught me one thing clearly: a flat network is not a network design, it is the absence of one.

The problem I had encountered before was that services exposed on local ports were reachable by anything on the same network. Bypassing authentication was sometimes as simple as hitting the direct address and port instead of going through the reverse proxy. This is not a hypothetical. It happened.

Beyond that, I had three distinct concerns that shaped the segmentation design.

The first was service isolation. I did not want client devices to reach service infrastructure directly. I also did not want services to communicate with each other laterally. Traffic between segments should pass through the reverse proxy, not through direct connections.

The second was IoT devices. Some devices in the house run closed-source firmware with unclear data practices. Smart appliances and home automation hardware from certain manufacturers phone home in ways that are not transparent. I was not primarily concerned about intrusion. I was concerned about what data was leaving, and where. Placing these devices in isolated segments where they cannot observe other network traffic is a meaningful constraint, even if imperfect.

The third was cameras. Surveillance cameras are a specific case. The risk of unauthorized access, including from firmware vendors or cloud providers, is real enough to warrant complete isolation: no internet access, no cross-segment reach, no exposure outside what the NVR software needs to receive the video stream.

---

## Segment design

The result is a set of distinct logical zones, each with a specific scope:

The **management segment** carries only infrastructure: servers, switches, access points, backup systems, and out-of-band management devices. It is never reachable from client networks by default.

The **server segment** hosts all service containers and virtual machines. Client devices do not have direct access here. They reach services through a reverse proxy that sits inside this segment. Traffic flows in one direction: clients reach the proxy, the proxy reaches the appropriate backend. The management segment remains separate, and its interfaces are accessible only through the administrative VPN tunnel, not through the proxy.

The **trusted segment** is for personal devices that need broad access to services. The **users segment** is for family devices, with internet access and selective reach to specific services.

IoT devices are split across two zones depending on whether they require internet connectivity. Those that do not are placed in a fully isolated zone with no outbound path whatsoever. Those that do are allowed outbound internet access but cannot reach any other internal segment.

Cameras have their own dedicated zone: isolated from everything, with no internet access. The only allowed traffic is the inbound stream pulled by the NVR.

Smart media devices and a guest wireless network complete the picture, each with appropriately limited reach.

The network operates on a default-deny posture: inter-segment traffic is blocked by default, and every communication path requires an explicit firewall rule

---

## Remote access

Two separate VPN tunnels run directly on OPNsense, providing different levels of access.

One is for infrastructure management: it reaches the server and management segments and is used for operating the homelab directly. The other is for general access: it reaches only services exposed through the reverse proxy, and is used when connecting from outside the home network.

The separation matters because administrative access and user access are different threat surfaces. A compromised device on the administrative tunnel would have direct access to the hypervisors. The two-tunnel design keeps those surfaces separate without requiring two physical endpoints.

---

## What operating this actually teaches

The value of building and running this infrastructure is not the infrastructure itself.

It is the operational experience that comes from being the only person responsible for every layer of the stack, from the physical cabling to the application running inside a container. There is no ticket to escalate. There is no network team to call. When something breaks, the gap in understanding becomes immediately visible, and filling it is the only path forward.

This is a different kind of learning from reading documentation or following a tutorial. When you misconfigure a firewall rule and lock yourself out, you understand stateful packet inspection in a way that no explanation produces. When you debug why two services cannot communicate and trace it back to a missing DNS override, you understand the relationship between name resolution and service discovery concretely.

In professional contexts, particularly in public sector digital governance, systems are designed and operated by specialists. The people responsible for policy rarely have direct visibility into how those systems behave at the architectural level. Having operated a network where every decision was mine, including the consequences of bad ones, gives me a different frame for reading architecture documentation, evaluating vendor claims, and understanding where the real constraints in a system lie.

It does not replace specialized expertise. It provides a ground-level reference that makes that expertise easier to engage with.