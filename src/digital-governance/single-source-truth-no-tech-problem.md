---
layout: article
title: A Single Source of Truth Is Not a Technical Problem
created: 2026-03-27
keywords: data governance, organisational alignment, single source of truth, institutional trust, federated systems
excerpt: Why centralising authoritative data in federated institutional networks is fundamentally a coordination problem, not an architecture decision.
article_id: single-source-truth-no-tech-problem
---

## The promise

A citizen crosses an administrative boundary. The core state registry updates her record: new address, new jurisdiction, new assigned service node. The update propagates. And yet, when she presents herself at the local office the next morning, the system still shows the previous assignment. The desk operator apologises, checks manually, and resolves it. Nobody is surprised. This is how it works.

In highly regulated, multi-layered ecosystems, the idea of a single source of truth is often presented as a technical objective. Centralise the data. Remove duplication. Ensure consistency. The logic is appealing: if there is one authoritative copy, there can be no conflict.

In practice, it rarely works that way. Not because the technology is insufficient, but because the systems that maintain citizen data are embedded in institutional structures where duplication is not an accident. It is a consequence of how responsibility is distributed.

Understanding this changed how I think about data architecture in public systems. The problem is not how to store data. It is how organisations agree on it.

---

## Why local copies exist

Consider the typical architecture of a federated institutional network. At the top, a central authoritative ledger holds the canonical identity of every enrolled entity: name, fiscal identifier, residence, service assignment, jurisdictional membership. This is the reference. Below it, each peripheral administrative unit maintains its own copy of that data, enriched with locally managed fields: active entitlements, specialist authorisations, internal identifiers, operational flags that the central ledger does not track.

From the outside, these local copies look like redundancy. A data architect would see them as a problem to be eliminated. But they exist for reasons that are not immediately visible in a system diagram.

Local systems serve as verification layers. When the core state registry sends a notification that a citizen has changed address, or switched service provider, or moved to a different jurisdiction, the local system does not simply overwrite its record. It validates the incoming data against its own state. Some fields map cleanly. Others do not, because the local system tracks things the central record does not, or represents them differently. In some cases, the update triggers a re-verification workflow that takes hours or days.

Meanwhile, the citizen walks into a local office. The desk operator sees the old record. Not out of negligence, but because the validation cycle has not yet completed. The local system is doing exactly what it was designed to do: verify before accepting. The inconsistency is real, but it is the cost of distributed responsibility, not a failure of the system.

Local systems also serve as operational buffers. If the central authoritative ledger goes down, edge authorities can continue to operate because they hold a working copy of the data they need. This is not elegant, but it is resilient. And in regulated public services, resilience is not optional.

Finally, local systems serve as accountability points. When a peripheral administrative unit manages a citizen's entitlements or authorisations, it does so as a data controller with specific legal responsibilities. Holding a local copy is not just a technical convenience. It is a consequence of the regulatory structure that assigns different institutions different roles over the same data.

---

## The notification model and its limits

The architecture I just described typically operates on a push model. The core state registry detects a change and sends a notification downstream to every local system that might be affected. Each local system receives, validates, and integrates the update on its own schedule.

This model has worked for years. It also has a structural problem: it scales duplication.

Every notification creates a new copy of the data at every receiving end. The more local service nodes exist, the more copies are maintained. The more copies exist, the more opportunities there are for drift: a notification that arrives late, a validation that fails silently, a local enrichment that conflicts with a subsequent update.

Over time, the gap between the central ledger and any given local copy becomes a function of timing and implementation quality. The system converges toward consistency, but never guarantees it at any given moment. For routine operations, this is acceptable. For cross-boundary workflows, where one institution needs to trust another institution's data in real time, it is not.

But the notification model's limitations become most visible not within a single federated domain, but across domain boundaries. Consider a citizen who moves from one autonomous jurisdiction to another. She registers with the new jurisdiction's service system and is assigned a new local provider. The new jurisdiction begins allocating resources for her primary services. The problem is that the old jurisdiction has no mechanism to learn that she has left. Its registry still lists her as an active entity. Her former provider is still on the books. The old jurisdiction continues to allocate resources for a service that is no longer being delivered.

The result is that the system pays twice for the same citizen's primary entitlements. Not because of fraud or negligence, but because two independent registries, each internally correct, have no shared reference to reconcile against. The old jurisdiction's data is not wrong. It is stale. And without a national-level source of truth that both jurisdictions query, there is no event that triggers the correction. The citizen moved. The data did not.

This is not a theoretical risk. It is a structural inefficiency embedded in any system where autonomous registries operate as independent authorities with no common upstream. The push model, which works tolerably within a single domain, breaks down entirely when the boundary to cross is between domains rather than between local service nodes.

The deeper problem is that the push model encodes a specific assumption about how data should flow: the centre distributes, the periphery absorbs. In practice, local systems do not just absorb. They interpret, enrich, and adapt. The notification is a starting point, not a conclusion.

---

## The architectural shift: from copies to queries

When I started working with systems that were moving beyond this model, the direction was clear in principle but difficult in practice. The shift is from replication to access: instead of maintaining synchronised copies, systems query a shared authoritative source directly when they need current data.

The logic applies at every scale. Within a domain, peripheral units stop maintaining shadow copies and query the core state registry instead. Across domains, the registries themselves stop operating as independent authorities and integrate with a higher-order national ledger that provides the shared reference they lacked. The cross-boundary double allocation described above becomes structurally impossible: when a citizen registers in a new jurisdiction, the national ledger reflects the change, and the old jurisdiction's system sees it the next time it queries.

In architectural terms, this is a move from push to pull. Sources stop sending notifications. Downstream systems stop maintaining copies of data they do not own. When a desk operator needs to verify a citizen's identity or service assignment, the system makes a real-time API call to the authoritative source and gets the current state.

This eliminates an entire category of consistency problems. There is no lag between the source and the downstream record, because there is no downstream record for that data. The source is queried, not copied. But the trade-off is direct: the pull model eliminates inconsistency at the cost of systemic dependency. Every downstream system now relies on the authoritative source being available, correct, and fast enough for real-time use.

This is where the concept of trust becomes central, and not in the technical sense of TLS certificates or API authentication. The trust that matters is institutional. The authoritative source must be highly available, because every downstream system depends on it for routine operations. The API must be well-governed, because every query carries an implicit agreement: the consuming system is accepting the response as authoritative without local validation. And the transition itself must be managed carefully, because dismantling local copies means removing the operational buffers and verification layers that those systems provided.

In the push model, trust was distributed. Each local system trusted its own copy, verified on its own terms. In the pull model, trust is centralised. Every actor must agree that the source is authoritative, that its data is correct, and that its availability is guaranteed. This is not a technical configuration. It is an institutional commitment.

This is where the real difficulty lives. The technical implementation of an API is straightforward. The institutional agreement required to trust that API — to accept that the data it returns does not need local verification, to restructure workflows that depended on having a local copy — that is organisational work, not engineering work.

---

## What makes convergence possible

A single source of truth does not emerge from architecture alone. I have seen systems where the technical layer was well-designed but the institutional alignment was missing, and the result was a central registry that existed alongside local copies that no one was willing to dismantle. The architecture was correct. The organisation had not changed.

What actually enables convergence is not a better database or a faster API. It is a prior agreement on who owns what. Consider a simple field: a citizen's entitlement status. The central ledger knows whether the citizen exists. The peripheral unit knows whether that citizen qualifies for a specific entitlement, because it holds the supporting documentation. If both systems maintain the field independently, they will eventually disagree. The only way to prevent that is to decide, before writing any code, that the entitlement field belongs to one system and one system only, and that every other system queries it rather than copying it.

This sounds obvious. In practice, it requires negotiations that have nothing to do with technology: which institution accepts liability for an incorrect value, what happens when a query fails and the data is needed for a time-sensitive decision, who pays for the infrastructure that makes real-time access possible. These are governance questions, not engineering questions. And they must be answered for every field in the data model, not just the easy ones.

The principle known as "once only" — where a citizen should never be asked to provide information the administration already holds — captures the aspiration well. It has been legislated in multiple jurisdictions. The legal basis exists. What is often missing is the trust infrastructure underneath: shared operational practices, institutional willingness to treat another administration's data as authoritative, and a culture that prioritises the citizen's experience across organisational boundaries rather than within them.

---

## The same lesson, in a different system

I have encountered this pattern in a completely different context: my own homelab infrastructure. In [The Commit Is the Deploy](/infrastructure/zero-to-homelab/gitops-and-secrets/), I described how I moved from manually configured services on each host to a single Git repository that defines the complete state of the infrastructure.

The parallel is closer than it might seem. Before the repository, each host had its own configuration, its own copy of environment variables, its own version of what was supposed to be running. The configurations would drift. Updates would happen on one host and not another. The gap between intended state and actual state grew silently. It was the same push model at a smaller scale: I would make a change and propagate it manually to each host, hoping for consistency.

The repository solved this by becoming the single source of truth. Hosts no longer maintain their own state. They query the repository and converge to whatever it defines. A commit is a deploy. There are no local copies to reconcile.

But even in that context, the hard part was not writing the deploy script. It was deciding to trust the repository as authoritative, to accept that local modifications would be overwritten, to restructure the operational workflow around a centralised definition rather than distributed improvisation. Trust, again, was the bottleneck. Not trust in the technology, but trust in the decision to give up local control.

The technical layer was the easy part. The shift in how I operated the system was the real change.

---

## Closing

A single source of truth is often described as a data architecture goal. In reality, it is a coordination problem. Technology can support it, but cannot create it.

The systems I have worked with — both in federated institutional networks and in infrastructure — taught me the same thing: duplication exists because responsibility is distributed, and it persists because trust is not. Eliminating duplication without first building the institutional trust that replaces it does not create a single source of truth. It creates a central system that no one fully relies on, surrounded by local copies that everyone still depends on.

The path forward is not centralisation for its own sake. It is the slower work of defining who owns what, who validates what, and what it means to accept someone else's data as authoritative. When that trust is established, the architecture follows naturally. When it is not, no amount of engineering will compensate.
