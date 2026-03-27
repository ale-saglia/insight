---
layout: article
title: A Single Source of Truth Is Not a Technical Problem
date: 2026-03-27
category: digital-health
permalink: /digital-health/single-source-truth-no-tech-problem/
---

## Context

In healthcare systems, the idea of a *single source of truth* is often presented as a technical objective.

Centralize the data. Remove duplication. Ensure consistency.

On paper, the solution is straightforward.

In practice, it rarely is.

Because the problem is not how to store data — it is how systems agree on it.

---

## Why duplication exists

Healthcare data is not just a technical asset. It is tied to responsibility.

Different institutions operate on the same data, but with different roles:

- some are responsible for primary information (e.g. identity, residence)  
- others manage operational relationships (e.g. service access, assignments)  

This creates a distributed ownership model.

Each actor needs control over “their” part of the data — not just access to it.

Local systems are not an accident. They are a consequence of this structure.

---

## The hidden function of local systems

Local systems are often seen as duplication.

In reality, they act as:

- verification layers  
- operational buffers  
- accountability points  

Data does not simply “flow” into a central system. It is:

- checked  
- validated  
- contextualized  

before becoming authoritative.

Centralizing unverified data does not solve inconsistency — it scales it.

---

## Why centralization is hard

The difficulty is not technological.

It comes from the need to align:

- responsibilities  
- validation processes  
- operational constraints  

across multiple organizations.

Even when a central system exists, local adaptations persist because:

- processes differ  
- timing differs  
- incentives differ  

What looks like redundancy is often what keeps the system working.

---

## The shift: from replication to access

When systems evolve, the architecture tends to move:

- from replicated databases  
- to shared access through services  

Instead of synchronizing copies, systems query a common reference.

This reduces duplication, but introduces new constraints:

- dependency on availability  
- need for strict governance  
- tighter coordination across actors  

Removing copies simplifies data — but increases the cost of being wrong.

---

## What actually enables a single source of truth

A single source of truth does not emerge from architecture alone.

It requires:

- clearly defined ownership  
- explicit validation responsibilities  
- shared rules for data lifecycle  

When these are in place, the technical layer becomes simpler.

Without them, duplication is not a failure — it is the default.

---

## Closing

A single source of truth is often described as a data architecture goal.

In reality, it is a coordination problem.

Technology can support it, but cannot create it.

And without coordination, there is no such thing as a single source of truth — only multiple versions that temporarily agree.