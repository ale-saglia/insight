---
title: Reusing public data at the point of friction
created: 2026-06-17
keywords: digital governance, public administration, open data, OpenCUP, CUP,
  software reuse, local-first
excerpt: How cup-check turns OpenCUP data into a local-first operational control,
  and why the design choices matter for public-sector software.
category: digital-governance
article_id: cup-check-public-data-reuse
---

## The question

The idea for [cup-check](https://github.com/ale-saglia/cup-check) started from a small moment during a webinar.

The session was about experimenting with an artificial intelligence solution in an administrative context. At some point, a colleague asked whether AI could be used to validate CUP codes in bulk.

It was a good question, because it came from a real operational need. In public project reporting, especially around funded programmes and NRRP workflows, a malformed or wrong CUP can block checks, slow down uploads, and generate corrections that should have been caught earlier. When the list has hundreds or thousands of rows, manual lookup is not a serious answer.

But the question also exposed a pattern I find increasingly common: when an organisation lacks small usable tools, every repetitive administrative problem starts to look like an AI problem.

This one did not.

A CUP is not an ambiguous text to interpret. It is a structured administrative identifier. It has formal rules. There is a public data source, OpenCUP, that can be reused within its declared limits. The first answer should not be prediction. It should be deterministic control, explicit limits, and a workflow that can be inspected.

That is the space cup-check tries to occupy.

---

## What the tool does

cup-check is a local-first tool for checking Italian CUP codes before administrative reporting, uploads, or downstream validation.

It has two surfaces: a static [web app](https://ale-saglia.github.io/cup-check/) and a [Python package](https://pypi.org/project/cup-check/). The web app validates pasted lists, CSV files, and spreadsheets. It checks the formal structure of each CUP and, when the static OpenCUP dataset is available, verifies whether the code is present in the published OpenCUP perimeter. It can also extract CUP codes from PDF invoices and FatturaPA XML files, then pass them to the same validator.

Those features are useful, but they are not the point of the project.

The point is the design posture.

cup-check does not claim to certify that a project exists. It distinguishes a formally valid CUP from a CUP found in the available OpenCUP mirror, and it keeps the "not found" case cautious: not found in the dataset does not mean nonexistent. It means: verify.

That distinction matters. Public-sector software often fails not because it is too modest, but because it becomes too confident exactly where the institution still needs traceability, legal certainty, or human review.

---

## Reuse is not publication

In an [earlier article](/digital-governance/data-pa-digital-transition/), I summarised the core argument of my bachelor's thesis: Italian public administration has built a mature normative framework around data, but still struggles to turn that framework into organisational capacity.

Open data is one of the clearest examples.

Publishing a dataset is necessary. It is not sufficient.

If a public dataset exists, but the people who need it still run slow manual searches, copy values between portals, or invent workarounds in spreadsheets, then the data is formally open and operationally distant. It is available in the abstract, not at the point where the process breaks.

cup-check is a small attempt to close that distance. It takes a public dataset, OpenCUP, and turns it into an operational control that can live where the work already happens: before a transmission, before a report, before a batch of documents enters a more expensive validation flow.

This is why I think of it as both a real service and a proof of concept for public data reuse. Not a demo in the "look what could exist someday" sense — a working tool. But one that also demonstrates a principle: reuse becomes meaningful when public data is turned into a capability that reduces friction inside a real process.

---

## Why local-first matters

The local-first architecture is not an aesthetic choice.

The files the user loads — CSV, XLSX, pasted lists, PDFs, XML invoices — are processed in the browser. The app does not upload CUP lists, documents, or reports to an application backend. The OpenCUP dataset is fetched as a public static asset, cached locally, and used for lookup on the user's machine.

That choice has consequences.

First, it shrinks the privacy and governance surface. Even when CUP codes are not personal data, administrative files can carry contextual information that should not be sent to a service that does not need it.

Second, it keeps operational cost close to zero. A static web app on GitHub Pages, with versioned dataset assets, is a very different maintenance object from a server-side application that needs hosting, credentials, monitoring, and incident response.

Third, it makes failure less dramatic. If the dataset is unavailable, the formal validator still works. If the browser holds a cached dataset, checks continue offline within the limits of that cache. The tool degrades instead of disappearing.

This is the kind of boring architecture public administration often needs more of: proportionate, inspectable, cheap to run, and clear about what it can and cannot do.

---

## Product governance as a feature

The repository is structured so that behaviour is not hidden inside the interface — and this, more than any single feature, is the actual argument of the project.

The repository is public and acts as the single source of truth. Validation rules are backed by shared fixtures, so expected behaviour is explicit before it is implemented. The web app and the Python package are tested against the same expectations, which keeps two versions of the same rule from drifting apart. Architectural decisions live in ADRs instead of in implicit memory. Releases follow SemVer, and software releases and OpenCUP dataset releases are kept as separate objects. The dataset manifest is part of the contract between source data, generated assets, and consuming clients.

The licence is a governance decision too. cup-check uses [EUPL-1.2](https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12), not a generic permissive licence, because the project is meant to be read in a European public-sector reuse context. That does not make adoption automatic, but it makes the legal and institutional posture legible: the tool is not just "open source" in the abstract, it is shaped so that another public body, supplier, or technical team can inspect it, evaluate it, reuse it, or replace it without asking a vendor for permission.

These details may sound internal. In governance terms they are part of the product. If an administration wants to rely on a tool, it should be able to ask basic questions:

- What rules are being applied?
- Where does the data come from?
- When was the dataset updated?
- What happens when the source is missing?
- Can the result be reproduced?
- Can another team inspect, fork, adapt, or replace the tool?

For a consumer app, these questions feel excessive. For public-sector software, they are the minimum conditions for trust.

---

## The AI angle

The project did not come from opposition to AI.

In fact the tool already uses machine learning where it is proportionate: OCR for scanned PDF invoices. When a file has no usable text layer, the extraction step falls back to local OCR and passes the detected CUP codes to the validator. That is a reasonable use of probabilistic technology — reading a noisy document, not deciding whether an administrative identifier exists.

AI may also help around the edges of a workflow like this: mapping columns, summarising anomalies, guiding someone through a confusing administrative file. There are places where probabilistic systems reduce friction.

But the core validation of a structured identifier is not one of them.

When the task is deterministic, the system should be deterministic. When the source has a defined perimeter, the tool should declare that perimeter. When a negative result is uncertain, the interface should say "to be verified", not pretend to know more than it does.

The question is not whether AI can produce an answer. It is what kind of assurance the process requires. For CUP validation the answer is simple: explicit rules, exact lookup where possible, cautious outcomes, and a human-verifiable chain from input to result.

---

## Small public software

cup-check is not a large system. That is part of why it interests me.

Much of digital transformation is discussed at the level of platforms, strategies, national infrastructures, and European regulatory frameworks. Those things matter. But administrative capacity is also built through small tools that make existing processes less fragile.

A spreadsheet check before upload.

A local extraction step before manual review.

A reusable library instead of copied validation snippets.

A public repository that documents not only what the tool does, but why it is built that way.

This is where the abstract language of data governance becomes practical. Not in a new slogan about interoperability, but in a small reduction of operational uncertainty.

The broader lesson is the one from my thesis, seen from the other side. The problem is not only whether public administration has data, rules, or digital strategies. It is whether those elements become usable capacity inside real workflows.

cup-check does not solve that problem. It is far too small for that. But it is an example of the direction I think public-sector software should take: reuse public data, distribute through the cloud for consistency, run locally for privacy, expose the rules, state the limits, avoid unnecessary infrastructure, and make the next administrative action easier than it was before.

That is not spectacular.

It is just useful.

And useful is often where governance begins.