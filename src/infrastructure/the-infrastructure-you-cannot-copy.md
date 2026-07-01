---
title: The Infrastructure You Cannot Copy
created: 2026-06-30
modified: 2026-06-30
keywords: ai sovereignty, infrastructure, semiconductors, supply chain, data centres, energy, lithography, public administration
excerpt: A companion to "Sovereign AI Is Not a Flag". At the model layer, sovereignty is fragile because everything copies. At the physical layer, dependence becomes harder to escape because almost nothing does.
article_id: infrastructure-you-cannot-copy
---

The previous piece argued that sovereign AI is not a flag on a model. It is a dependency you can name, govern and survive losing.

This is the other side of that argument.

At the model layer, everything copies. Weights can leak, be distilled, be reproduced, be wrapped, be orchestrated or be replaced within a generation. That makes sovereignty fragile, but it also gives system designers room to manoeuvre. If a model is unavailable, a resilient architecture can sometimes route around it.

At the physical layer the situation is reversed. Almost nothing copies. A data centre cannot be forked. A fab cannot be mirrored. A lithography ecosystem cannot be cloned from a repository. The deeper one moves down the stack, the less sovereignty looks like ownership and the more it looks like continued access to flows that nobody controls alone.

## In the power meter

In Memphis, the argument became visible in the most literal way possible. xAI's Colossus data centre needed far more electricity than the existing grid connection could immediately provide, so the company used gas turbines to supply power while the site expanded. Environmental groups and civil-rights organisations challenged the operation, alleging that turbines had been run without the required air permits [1] [2] [3].

I find that story clarifying because it shows where the argument about sovereign AI actually lives. Not in the model card. In the power meter.

A frontier model is a file. The thing that trains it and serves it is a facility that consumes electricity at the scale of industrial infrastructure. The first hard limit on anyone's AI ambition is not whether they can fine-tune a model. It is whether the grid can feed the machine room.

Power, though, is still a wall that can sometimes be bought through. You can sign long-term energy contracts, build substations, colocate with generation, burn gas, absorb delays, or accept legal and reputational costs. That does not make it easy, but it makes the constraint legible.

The deeper walls are less flexible.

## A stock that drains

Start with the hardware. The accelerators that train and serve AI are not durable possessions in the ordinary sense. Under heavy data-centre workloads they depreciate quickly, and even the accounting treatment of AI GPUs has become a live financial question for firms and investors [4]. Industry estimates on useful life vary, but the general point is simple: compute is not a pile of metal that remains strategic forever [5].

It is a stock that drains.

That changes what "owning compute" means. The accelerators in a rack are not sovereignty. They are a temporary buffer against dependence. The strategic question is whether you control the pipeline that replaces them when they age, fail, become uneconomic, or fall behind the next generation of workloads.

At that point the conversation stops being about procurement and starts being about industrial flows.

## A flow you cannot copy

Those flows narrow quickly.

Advanced AI chips depend on leading-edge semiconductor manufacturing. TSMC remains central to that layer, and AI demand has strengthened rather than weakened its position in advanced nodes [6]. ASML, in turn, is the critical supplier of the lithography systems used to manufacture the smallest and most complex chips, and it has identified AI as a long-term driver of demand for its machines [7].

The core bottleneck is not a secret recipe hidden in a single vault. It is worse than that. It is a distributed industrial capability.

An EUV lithography system is not a blueprint that can simply be executed. It is a machine the size of a bus, shipped in dozens of containers, assembled from specialised subsystems across a global supplier network, using light generated from tin droplets and guided through optics of extraordinary precision [8]. ASML remains the sole commercial maker of EUV systems, and even its own advances in EUV light-source power are described as multi-year engineering programmes rather than simple product updates [9].

That is why copying is the wrong mental model. Stealing a design would not transfer the capability. It would hand you the parts list for an ecosystem. The hard part is not knowing that the machine exists. The hard part is reproducing the people, suppliers, process knowledge, service organisation, metrology, software, materials and tacit operational learning that keep it useful.

## What a crisis actually does

This is where the more dramatic narratives become less useful.

The clean question is not whether someone could seize a fab, steal documents or obtain tools by force. The cleaner question is whether the capability survives disconnection from the ecosystem that keeps it alive.

A leading-edge fab is not an asset you capture and operate in isolation. It is a just-in-time node that survives only while connected to external service engineers, spare parts, ultra-pure chemicals and gases, software updates, process support and institutional knowledge.

EUV systems are not machines that can simply be turned on and left alone. They require continuous servicing and troubleshooting by highly trained specialists. Reuters reported that ASML opened a technical academy in Phoenix to train more than a thousand engineers per year to service DUV and EUV systems, with basic maintenance training measured in months and more advanced repairs requiring longer preparation [10].

That is the neutral version of the point, and it is stronger than the geopolitical version. The capability is not contained in the factory building. It is contained in the flow around the factory.

So the realistic shape of a crisis is not that an aggressor captures the tools and out-produces the world. It is that the node loses the ecosystem that keeps it alive. The fab may remain physically standing, but capability decays as tools fail, consumables run out, process windows drift, spare parts become unavailable, and the people able to restore yield are no longer present.

Seizing the node does not transfer sovereignty. It interrupts the flow that made the node useful.

## The asymmetry under everything

This is the mirror image of the model layer.

At the level of models, sovereignty is fragile because capability copies. Weights leak, get distilled, get reimplemented and get wrapped behind new interfaces. That creates risk, but it also creates substitutability.

At the level of fabrication, sovereignty is fragile because capability does not copy. You can mirror a registry. You cannot mirror a fab. The very quality that makes the physical layer hard to steal is the quality that makes it hard to escape.

That leaves one honest lever, and it is not self-sufficiency. No public administration is going to conjure a domestic leading-edge fab. Even national reshoring programmes relocate parts of the chain while remaining dependent on specialised suppliers, tools, skills and materials.

What remains is resilience.

Resilience means strategic stock where appropriate. It means diversified access among trusted partners. It means procurement that treats hardware replacement cycles as a governance question rather than an afterthought. It means designing workloads that can degrade gracefully, run on lower tiers of compute, or continue when the most advanced accelerators are unavailable. It means running infrastructure cooler, slower and longer when that is the more sovereign choice.

My homelab taught me the small version of this years ago. When I designed it, I wanted three nodes. Energy costs pushed me to two. The binding constraint on my own modest sovereignty was never the software, which I could reshape, but the power bill and the hardware I could afford to keep alive.

States are learning the same lesson at a scale where the power is a gas turbine and the hardware is an island's worth of fabs.

The first piece ended on a dependence you can name and survive losing. This is the other kind. At the bottom of the stack sits a dependence you can name precisely, document fully, and still not survive losing on any timescale that matters.

Sovereignty, at the infrastructure layer, is not something you own. It is something you are, for now, still connected to.

## Sources

All sources accessed 30 June 2026.

1. Reuters, "NAACP sues Musk's xAI, alleging illegal operation of gas turbines". https://www.reuters.com/sustainability/climate-energy/naacp-sues-musks-xai-alleging-illegal-operation-gas-turbines-2026-04-14/
2. Politico, "Elon Musk's xAI in Memphis: 35 gas turbines, no air pollution permits". https://www.politico.com/news/2025/05/06/elon-musk-xai-memphis-gas-turbines-air-pollution-permits-00317582
3. Earthjustice, "Illegal pollution from data center power plants shouldn't harm our communities. We're suing xAI". https://earthjustice.org/case/xai-illegal-gas-power-plant-data-center-colossus
4. CNBC, "The question everyone in AI is asking: how long before a GPU depreciates?". https://www.cnbc.com/2025/11/14/ai-gpu-depreciation-coreweave-nvidia-michael-burry.html
5. Tom's Hardware, "Datacenter GPU service life can be surprisingly short, only one to three years". https://www.tomshardware.com/pc-components/gpus/datacenter-gpu-service-life-can-be-surprisingly-short-only-one-to-three-years-is-expected-according-to-unnamed-google-architect
6. Reuters, "TSMC raises revenue forecast on bullish outlook for AI megatrend". https://www.reuters.com/world/asia-pacific/tsmc-q3-profit-expected-set-record-ai-spending-boom-2025-10-15/
7. Reuters, "ASML sees AI demand as long-term growth driver in 2025 annual report". https://www.reuters.com/world/china/asml-sees-ai-demand-long-term-growth-driver-2025-annual-report-2026-02-25/
8. Reuters, "The $250 million ASML 'printer' behind Nvidia's chips". https://www.reuters.com/world/asia-pacific/250-million-asml-printer-behind-nvidias-chips-2026-01-28/
9. Reuters, "ASML unveils EUV light source advance that could yield 50% more chips by 2030". https://www.reuters.com/world/china/asml-unveils-euv-light-source-advance-that-could-yield-50-more-chips-by-2030-2026-02-23/
10. Reuters, "ASML launches technical academy in Phoenix to train in-demand engineers". https://www.reuters.com/world/asia-pacific/asml-launches-technical-academy-phoenix-train-in-demand-engineers-2025-11-20/
