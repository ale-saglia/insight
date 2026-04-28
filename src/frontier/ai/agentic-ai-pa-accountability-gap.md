---
title: The accountability satisfies the citizen, not the agent
created: 2026-04-14
keywords: agentic AI, public administration, accountability, explainability, open
  government, interoperability, institutional governance, AI Act
excerpt: Agentic AI promises to transform government. But in a system built on explainability
  and open government, where every decision must be traceable and attributed, where
  does the agent end and the bureaucrat begin?
article_id: agentic-ai-pa-accountability-gap
---

Every administrative act in Italy must carry a motivation. Not a summary, not a label: a traceable chain of reasoning that a citizen can read, understand, and challenge before a judge. This principle is not a bureaucratic formality. It is the mechanism through which public power remains accountable.

Agentic AI, by design, operates differently. It pursues outcomes through statistical inference, adapts through feedback, and can coordinate across systems at a speed no human process can match. What it cannot do, today, is explain itself in a way that satisfies the institutional standards that public administration is built on.

Recently, AgID Academy hosted a webinar that put this tension at the centre: autonomy on one side, responsibility on the other. The session drew on a recent vision paper, [*The Agentic State: Rethinking Government for the Era of Agentic AI*](https://agenticstate.org), one of the most comprehensive attempts to date to think through what agentic AI means for government, not just as a technology question but as an institutional one. It is worth reading in full.

What follows is not a critique of the paper. It is an attempt to ground some of its arguments in the specific reality of Italian public administration, where I work, and where some of the questions the paper raises become particularly sharp. The core of my argument is simple: the factors that limit agentic AI in public administration today are not primarily technical. They are institutional, legal, and infrastructural. And addressing them is a prerequisite, not an afterthought.

---

## The levels matter

One of the paper's most useful contributions is a taxonomy of agent capabilities, borrowed from autonomous driving, ranging from Level 0 (fully manual) to Level 5 (fully autonomous, no human involvement). Most real deployments today sit between Level 2 (AI classifies and prioritises, humans decide) and Level 3 (agents plan and adapt within defined domains, humans handle edge cases). Level 4, where agents act independently in bounded environments, exists only in constrained private-sector contexts. Level 5 remains research-only.

This distinction is worth keeping in mind, because the conversation around agentic AI tends to collapse these levels. When we talk about agents that *orchestrate complete workflows*, *anticipate citizen needs*, and *coordinate across organisational boundaries*, we are describing something between Level 3 and Level 4. When we talk about agents replacing bureaucratic processes entirely, we imply Level 4 or above. These are not the same thing, and the gap between them is where most of the difficult questions live.

---

## The explainability problem is not new, but AI makes it structural

Public administration has always operated under an explainability requirement. In Italian law, this takes the form of the *obbligo di motivazione*: every act affecting a citizen must state the factual and legal reasons behind the decision. But the principle is not uniquely Italian. It is a cornerstone of open government more broadly: the idea that public decisions must be transparent, traceable, and contestable.

The Open Government Partnership, the EU's own transparency frameworks, and the AI Act itself all converge on the same expectation: citizens have the right to understand how decisions that affect them are made. When a human official issues a decision, the reasoning can be reconstructed, examined, and challenged. The decision may be wrong, but the process is legible.

AI systems based on machine learning introduce a tension here. A large language model producing a decision or a recommendation does not reason the way a legal system expects reasoning to work. It does not apply a rule to a set of facts through a traceable logical chain. It generates outputs through statistical inference over learned patterns. The result may be correct. The process that produced it is, in the legal and institutional sense, opaque.

The paper engages with this directly. It calls for *structured explanations showing how inputs led to outputs, what alternatives were considered, and why specific approaches were chosen*. It proposes *layered transparency* for different audiences: plain-language summaries for citizens, reasoning traces for policy experts, algorithmic inspection for auditors. These are the right architectural goals.

The open question is timing. No current large language model can produce an explanation that satisfies the standard an administrative judge would require when reviewing a challenged act. Explainability research is advancing, but the gap between what a post-hoc interpretability tool can generate and what legal accountability demands remains significant. This is not necessarily a permanent condition, but it is the current one, and it is worth being honest about when planning deployments.

The mismatch is structural, not incidental. It applies everywhere open government principles are taken seriously, not only in Italy. And it means that the path from Level 3 agents (supporting human decisions) to Level 4 agents (making decisions within bounded autonomy) passes through unsolved problems in the explainability of AI systems, not just unsolved problems in their accuracy.

---

## Accountability requires a name

Beyond explainability, there is the question of responsibility.

The paper frames this well: *Attribution becomes complex when decisions emerge from interactions between multiple AI systems, training data, and real-time information flows rather than identifiable human judgement.* It proposes delegation frameworks, a kind of digital power of attorney, where officials formally authorise agents to act within defined scope, and remain accountable for the parameters they set.

This maps reasonably to a *human-on-the-loop* model, where an official supervises an autonomous system rather than approving each action. The paper acknowledges this will be the dominant model at scale, and the logic is sound.

Where it becomes difficult, at least in the Italian context, is that administrative accountability is not abstract. When a citizen appeals an act, the administration must identify who made the decision, on what authority, and through what reasoning. The *responsabile del procedimento* is not a metaphor. It is a named individual with a specific legal role.

Consider a concrete scenario: an agentic system processes a benefit application, cross-references five databases, applies eligibility criteria, and produces a denial. Who signed the act? The official who set the system's parameters six months ago? The one who approved its deployment? The one who received the output and clicked "confirm" without meaningful review?

The paper raises this question explicitly, and it is the right question to raise. The answer will likely require new legal frameworks that define what it means for a human to be accountable for a decision that was substantively made by a machine. That work has not yet been done in most jurisdictions. In Italy, where the procedural framework is particularly detailed, it will require careful legislative and jurisprudential evolution.

---

## Interoperability comes first

The paper's most compelling use cases for agentic AI involve cross-boundary coordination. A citizen reports house damage; agents orchestrate responses across insurance, emergency housing, building permits, and utilities. A business registration triggers identity verification, budget checks, and registry updates across departments, instantly.

These scenarios are genuinely appealing. They also depend on something that does not yet exist in most public administrations: reliable, real-time data interoperability across organisational boundaries.

I have [written before](/digital-governance/single-source-truth-no-tech-problem/) about why a single source of truth is not a technical problem but an organisational one. The same logic applies here, amplified. An agentic system that orchestrates across departments needs not just access to data, but semantically consistent, validated, authoritative data with clear ownership and governance.

In the Italian context, where regional health systems maintain separate patient registries, where municipalities run their own demographic databases, where interoperability between state systems often relies on batch file exchanges rather than real-time APIs, the infrastructure for cross-boundary agent orchestration is not yet in place. The agent would be navigating the same fragmentation that frustrates citizens today, just faster.

This is not a reason to dismiss the agentic vision. It is a reason to sequence the work correctly. The paper itself, in its data and privacy chapter, argues for treating data as critical infrastructure and calls for *ecosystem-wide governance* and *open by default* principles. That is exactly the right foundation. The point is that this foundation needs to come first, or at least in parallel, rather than after the agent layer is deployed.

And the gap is not only technical. Principles like *once only*, where the citizen should never be asked to provide information the administration already holds, have been legislated for years in Italy and across the EU. The legal basis exists. What is largely missing is consistent implementation: shared operational practices, institutional willingness to treat another administration's data as authoritative, and a culture that prioritises the citizen's experience across organisational boundaries rather than within them. Digital systems built to enable this, from interoperability platforms to shared registries, exist in many cases. But when they are adopted without the cultural shift that gives them meaning, they remain underused infrastructure: technically available, operationally irrelevant. The problem agentic AI would be asked to solve on the citizen-facing side is, in large part, the consequence of this gap between what is already normatively possible and what is actually practiced.

There is also a deeper question worth asking. Much of the bureaucratic complexity that agents would navigate is the residue of regulatory accumulation: layers of requirements from different eras, applied to modern contexts through incremental adaptation rather than structural redesign. Interoperability standards, API mandates, and above all legislative simplification would reduce the surface area that any agent needs to navigate. In some cases, the best use of resources is not building an agent that manages complexity, but removing the complexity that makes the agent necessary.

---

## Where agentic capabilities deliver value now

None of this means agentic AI has no place in public administration. It means the most productive deployments, at least in the near term, are likely to be those that work within existing accountability structures rather than against them.

There are domains where agentic capabilities at Level 2-3 can deliver real value today:

Internal workflow optimisation, where agents classify, route, and pre-process documents within a single administration, under direct human supervision. The paper's examples of invoice processing, risk-based inspection scheduling, and HR document analysis fall squarely here. These are high-volume, low-complexity tasks where the agent augments human capacity without displacing human authority.

Citizen-facing information services, where agents provide guidance, answer questions, and help citizens navigate procedures, without making binding decisions. This is the assisted interaction model: useful, lower-risk, and already in limited deployment in several countries. The paper's examples from Ukraine (Diia.AI) and Abu Dhabi (TAMM 3.0) show what this looks like at national scale.

Anomaly detection and quality control, where agents monitor data flows and flag inconsistencies for human review. In digital health, for example, an agent that identifies mismatches between regional and local patient records could accelerate reconciliation processes that currently take days.

Back-office coordination within a single organisation, where agents manage scheduling, resource allocation, and internal routing without crossing the organisational boundaries that make interoperability so difficult. The example from Goiás, Brazil, cited in the paper, where an agent reduced project review time from one year to a single week, falls into this category.

What these use cases share is that the agent operates within clear boundaries, a human retains decision authority, and the output is reviewable. They are not the full *Agentic State* the paper envisions, but they are real, deployable, and valuable.

---

## The conversation that matters

The webinar's framing put autonomy and responsibility side by side, and that pairing captures the core tension well. The paper does not shy away from it. Its governance chapter is one of the strongest in the document, proposing identity binding, behavioural attestation, preview windows, and citizen override mechanisms that go well beyond what most current discussions of AI governance attempt.

The Italian perspective within the paper is notably grounded: agents *fully under human control*, challenges around *scope of competence, regulations on procedural responsibility, and privacy, transparency, and accountability tools*. This is the language of people working through the operational detail of how a regulatory framework actually adapts to new technology.

The paper describes a broader vision: outcome-driven governance, self-composing services, and anticipatory government. That vision is worth engaging with seriously. The path toward it, though, runs through work that is not primarily technological: interoperability governance, legal frameworks for algorithmic accountability, legislative simplification, and a shared understanding of what explainability means when the decision-maker is a machine.

That work is less visible than deploying an agent. It is also what determines whether the agent, once deployed, actually serves the citizen or merely adds a layer of sophistication to a system that still does not function as it should.

The question is not whether agentic AI will become capable enough to operate in public administration. It probably will. The question is whether our institutional frameworks can absorb it without breaking the guarantees they exist to protect: that every decision can be explained, that every act has a responsible author, and that every citizen can challenge what the state does in their name. Those guarantees are not obstacles to innovation. They are the reason public administration exists at all.
