---
title: Sovereign AI Is Not a Flag
created: 2026-06-30
modified: 2026-06-30
keywords: sovereign AI, AI sovereignty, model dependence, export controls, public administration, digital governance, homelab
excerpt: Sovereign AI is often discussed as ownership of a model. The more useful question is what dependencies remain when the model changes, is withheld, copied or orchestrated.
article_id: sovereign-ai-is-not-a-flag
---

In late June, an Italian language model called Emma was launched as a contribution to national technological sovereignty. It had been trained and hosted in Italy and presented as an alternative to the American and Chinese systems most people now use without thinking. Within about a day it was withdrawn, after answering simple questions unreliably enough that the distance between how it had been presented and what it could actually do became the story [1] [2].

I do not want to make light of that. The ambition behind Emma was legitimate, and building national capability is slow, unglamorous work that deserves more patience than the internet usually grants it. What the episode exposed is not that one small model underperformed, because models underperform all the time. It exposed a confusion that runs through much of the discussion of sovereign AI. We treat sovereignty as something that can be declared at the level of the product, when it is really a property of the system that produces, maintains, audits and replaces it. The model was reportedly modest in size and in context window, and was framed as though the national label itself could loosen dependence on foreign AI infrastructure [3].

The question is not whether a model has a national flag on the splash screen. The question is what happens when the model disappears, is restricted, copied, degraded, replaced or outgrown.

## Where the question started

My own interest in independence from large platforms did not begin with geopolitics. It began when a terabyte of cloud storage I depended on was withdrawn, and I had to decide whether to keep paying or build something of my own. I chose to build, badly at first, and spent years learning that infrastructure is less about standing a system up than about keeping it standing.

That is the part the word "sovereignty" tends to hide. We treat it as a state you can declare, a flag you plant once. In practice it is a gradient of control that has to be maintained. The honest question is how far along that gradient you actually sit, and what it would cost you to slide back.

The same anxiety that pushes one person off a commercial cloud is now visible at the scale of states. What makes the current moment useful is that the main actors are answering the same question in different ways.

## Four answers to one question

The first answer is control through denial.

When access to frontier systems is limited at the request of a government, sovereignty belongs to the party that can decide who is allowed to use the capability. OpenAI's limited rollout of GPT-5.6, reportedly requested by the U.S. government, is an example of this logic [4] [5]. Anthropic's Mythos case points in the same direction: frontier models with serious cybersecurity capability are increasingly treated not simply as products, but as controlled strategic assets [6].

This is sovereignty as gatekeeping. It is real. If you hold the switch, you are sovereign. If you depend on the holder of the switch, you are not.

The second answer is sovereignty as portability.

Chinese laboratories and companies have pushed strongly in the opposite direction, releasing open-weight models that can be downloaded, modified and run outside a single vendor's platform. GLM-5.2 is a useful example: its release was discussed not only as a product launch, but as part of a broader shift in which powerful open models reduce the practical dependence on closed American systems [7]. Other Chinese companies have followed the same pattern, presenting open models as a way to build self-reliant AI ecosystems under chip and platform constraints [8].

For adopters, this looks attractive. Weights that can be run locally cannot be switched off by a provider. They can be inspected, adapted, quantised, hosted and embedded in systems that do not depend on a single API contract.

But portability is not independence. It moves dependence downward and sideways. You still depend on provenance, training choices, safety behaviour, licensing, hardware, inference costs and the ecosystem that keeps the model usable. Open weights reduce one dependence by accepting others.

The third answer is sovereignty as orchestration.

Sakana AI's Fugu technical report describes a family of orchestrator models that dynamically build agentic scaffolds and route work across a team of other LLM agents [9]. This is strategically interesting because it shifts the centre of control away from owning every model and toward coordinating multiple capabilities.

At first glance, that sounds like resilience. If one provider is weak, route around it. If one model is better at coding and another at reasoning, compose them. If capability is fragmented, build at the integration layer.

But orchestration is not the same thing as sovereignty. An orchestrator inherits the constraints of the systems it coordinates. If several providers restrict access at the same time, or change pricing, latency, policies or terms, the orchestrator does not escape those decisions. It only makes the dependency graph more sophisticated.

The fourth answer is sovereignty as label.

Emma belongs here, and of the four it is the most sympathetic case, because the intention behind it was the right one. The lesson is not about a company or a person. It is that a national model is not sovereign simply because it is national. It is sovereign only to the extent that it can be built, evaluated, sustained, corrected and described honestly. The question worth carrying away was never whether the model performed well on a given day. It was whether the claims made around it matched the capability that had actually been built.

A national label cannot substitute for evaluation. Hosting cannot substitute for capability. Rhetoric cannot substitute for documentation. A system that can state its limits, be tested against them and survive correction has started to earn the word. One that cannot has not, whatever flag sits on it.

## What a homelab taught me about all four

Running a small system over time gives you an unglamorous intuition that maps onto each of these cases.

Abstraction reduces lock-in. It does not remove dependence. When I moved services to containers, I made them portable, reproducible and easier to move between machines. I did not become independent of the registries those images come from, the upstream projects that maintain them, the package repositories they rely on, the silicon they run on, or the electricity that keeps the system alive.

What I gained was not independence. It was legibility.

I can name dependencies. I can decide which ones I tolerate. I can pin versions. I can mirror images. I can keep local backups. I can build enough redundancy to survive a provider disappearing or a service changing terms. The point of mirroring an image locally is not pride. It is that I have looked the dependence in the eye and chosen how much of it I am willing to tolerate.

That reframes the four answers.

Denial is sovereignty for the actor holding the switch. Open weights are portability bought with provenance and hardware risk. Orchestration is convenience that inherits the constraints of the systems beneath it. A national model is sovereign only to the extent that the industrial, technical and institutional capacity behind it is real.

None of these is sovereignty as a finished state. Each is a position on a gradient, with a different cost of sliding back.

## For public systems, the operative question

For anyone responsible for public digital infrastructure, the lesson is not to chase the most capable model. The most capable model can become unavailable, unaffordable, non-compliant or politically constrained. The lesson is to design so that the model remains a replaceable component rather than the foundation of the system.

That means documenting external dependencies. It means separating model choice from workflow design. It means being able to switch providers without rewriting the service. It means knowing which data can leave the organisation, which data cannot, and which functions must continue even when a frontier API is unavailable. It means describing system limits without embarrassment.

An administration that treats model choice as interchangeable, and that can state its dependencies openly, is more sovereign than one with a national flag on the interface and an underpowered model behind it.

Sovereign AI is not a flag you plant. It is a dependency you can name, govern and survive losing.

## Sources

All sources accessed 30 June 2026.

1. Smartworld, "Emma-5, l'IA italiana della sovranità tecnologica, è già offline". https://www.smartworld.it/news/emma-5-ia-italiana-chiusura-meme-sovranita-tecnologica.html
2. Today.it, "Abbiamo provato Emma, la prima AI sovranista italiana (già sospesa)". https://www.today.it/attualita/emma-prima-ai-sovranista-italiana.html
3. Pasquale Pillitteri, "Emma di Egomnia: cosa sa fare davvero l'LLM italiano". https://pasqualepillitteri.it/en/news/6180/emma-egomnia-italian-llm
4. CNBC, "OpenAI limits new AI models to 'trusted partners' at request of U.S. government". https://www.cnbc.com/2026/06/26/openai-limits-new-ai-models-to-trusted-partners-request-us-government.html
5. Business Insider, "OpenAI says access to its new GPT-5.6 model is limited at the US government's request". https://www.businessinsider.com/openai-gpt-5-6-limited-preview-us-government-ai-security-2026-6
6. CNBC, "Anthropic's Mythos model found vulnerabilities in classified U.S. government systems, official says: AP". https://www.cnbc.com/2026/06/23/anthropics-mythos-model-found-vulnerabilities-in-classified-us-government-systems-official-says.html
7. Axios, "China's new open-source model accelerates AI hacking threat". https://www.axios.com/2026/06/25/china-glm-52-open-source-hackers
8. South China Morning Post, "China debuts biggest AI model trained on local chips, as Meituan releases LongCat-2.0". https://www.scmp.com/tech/tech-trends/article/3358854/china-debuts-biggest-ai-model-trained-local-chips-meituan-releases-longcat-20
9. Sakana AI, "Sakana Fugu Technical Report". https://arxiv.org/abs/2606.21228
