---
title: Building compliance tools before I knew what governance meant
created: 2026-03-28
keywords: compliance, process governance, digital transformation, software architecture,
  organizational systems
excerpt: Two software projects that taught me more about digital transformation through
  failure than any textbook could. A retrospective on naive tool-building.
article_id: build-compliance-tool-before-i-know-compliance
---

Between 2019 and 2021, I built two software tools for two very different organisations facing the same underlying problem: they were growing faster than their ability to keep track of their own obligations.

Neither project ended the way I hoped. One was eventually abandoned due to accumulated technical debt and no one left to maintain it. The other was never really adopted at all.

Both taught me more about digital transformation than I expected, not because of the code I wrote, but because of what happened when I tried to introduce it.

---

## DESU: when a spreadsheet stops being enough

[DESU](https://github.com/ale-saglia/desu) stands for *deadline support*. I built it for a compliance consulting firm I was collaborating with as an external contractor.

The firm provided RSPP (workplace safety officer) consultancy services to a portfolio of clients. As the client base grew past a hundred accounts, so did the volume of active engagements: each client had its own contract, its own inspection schedule, its own renewal dates, its own billing cycle. The team was tracking all of it in spreadsheets.

The problem was not incompetence. It was scale. Spreadsheets work fine for ten clients. At a hundred, with multiple overlapping deadlines per client per month, the cognitive overhead becomes unsustainable. Things start slipping through.

I built DESU to address this directly. The architecture was deliberately simple: a Java/JavaFX desktop client with a PostgreSQL backend, a DAO layer for clean data access, and a set of server-side Python scripts for automated email notifications. Every month, the system would query the database and send a digest of upcoming billing deadlines and expired engagements that still lacked an invoice, the two failure modes the firm cared most about.

```java
subject = "Incarichi da fatturare per il mese di " + calendar.month_name[datetime.now().month]
```

It was not sophisticated. But it worked, and it addressed a real operational pain point.

I chose to make it open source for a specific reason: I was an external contractor, not a permanent employee. I knew my engagement would end, and I wanted the firm to have the option to hand the project to another developer without being locked into me. FOSS was the cleanest exit strategy I could think of. The code would remain accessible and modifiable by whoever came after.

As far as I know, DESU stayed in use for several years after I left. It eventually stopped being maintained and was replaced, I believe by Notion. Which is entirely reasonable: a general-purpose tool with a managed update cycle is a better fit for a small firm than custom software that requires a developer to evolve it.

---

## The second project: when the problem is not technical

The second project started from a different context. After competing in a business innovation challenge at the local Junior Enterprise, where my team worked on a digital transformation strategy for traditional Piedmontese craft companies, I stayed in contact with one of the firms involved.

The company was a small artisan business. Post-competition, I volunteered to help translate some of the strategy we had presented into something concrete: a lightweight inventory management tool to replace a manual process that was becoming unwieldy as production volumes grew.

I built a small JavaFX application with a CSV-backed data model. CSV as a persistence layer is a pragmatic choice when you do not want to introduce a full database into a context where no one has the skills to maintain one. The tool needed to be operable by non-technical staff without infrastructure overhead.

The project never made it into production.

It was not a technical failure. The company's attention was almost entirely focused on the present: on day-to-day operations, on immediate orders, on this week's production run. Any investment of time and energy that did not directly address an immediate operational need felt like a distraction. Digital transformation, even a very modest one, requires a certain willingness to invest in the future. That willingness was not there.

I do not say this as a criticism. Small craft businesses operate under real constraints, and the instinct to focus on what is in front of you is often rational. But it was the first time I encountered something I would later come to recognise as one of the most consistent patterns in digital transformation work: the gap between what an organisation *could* do and what it is actually *ready* to do is almost never a technical gap.

---

## What I took from both projects

Looking back, both projects were fundamentally about the same thing: how do you make obligations, deadlines, and data flows visible and manageable in an organisation that has more complexity than its current systems can handle?

DESU was a compliance tracking system. It modelled regulatory relationships between entities, surfaced obligations before they became failures, and tried to make accountability legible to the people responsible for it.

The second project failed for reasons that are entirely familiar in public sector digital transformation: competing priorities, short time horizons, and the difficulty of convincing an organisation to invest in infrastructure that will not pay off until later.

What neither project gave me at the time was a language for what I was actually doing. I was decomposing processes, identifying data flows, mapping responsibilities. I was doing it instinctively, based on operational observation, without any formal framework.

A few years later, working through a university course on process modelling, I finally had a name for it. BPMN gave me a notation and a way of thinking that made explicit what I had been doing informally. Seeing it formalised did not change how I approached problems, but it clarified why certain approaches worked and others did not. The inventory tool had failed partly because I had never properly modelled the process I was trying to support. I had built a solution before understanding the problem well enough.

That lesson, more than anything else, shapes how I approach governance work now. The code is the easy part. Understanding the process it needs to serve is where the real work is.
