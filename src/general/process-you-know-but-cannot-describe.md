---
title: "The process you know but cannot describe"
created: 2026-03-30
modified: 2026-04-11
category: general
keywords: process modeling, BPMN, business process, governance, formalization
excerpt: Formalizing a process you know intimately but cannot articulate. A case study in process modelling using BPMN and the Italian Highway Code.
permalink: /general/process-you-know-but-cannot-describe/
layout: article
---

In an [earlier post](https://insight.ale-saglia.com/general/build-compliance-tool-before-i-know-compliance/), , I wrote about two software projects I built before I had a formal framework for what I was doing. The conclusion was simple: building tools to manage deadlines and track compliance obligations was, in retrospect, a primitive attempt at process governance. The code was the easy part. Understanding the underlying process well enough to model it was the real work.
 
I also mentioned a university course on process modelling that finally gave me a language for what I had been doing instinctively. This is that story.
 
---
 
## The process I already knew
 
For the course assignment, I chose to model a process I had been living inside for four years: the sanctioning procedure under the Italian Highway Code (*Codice della Strada*), as implemented at the small municipality where I worked as a local police officer.
 
It was a deliberate choice. I was not interested in inventing a fictional process for the exercise. I wanted to see what happened when I tried to formalise something I already knew intimately, from the inside.
 
The process, in summary: a traffic violation is detected, documented, and notified. The recipient then has several possible responses, each triggering different sub-flows. They can pay the reduced fine within 60 days. They can submit a formal defence. They can appeal to the Justice of the Peace or the Prefect. If nothing happens, the debt is registered and transferred to a collection agency. If there is a formal error in the verbal, the process can be corrected or annulled.
 
I knew all of this. I had run every path in that diagram personally. I could have described it in prose in five minutes.
 
What I could not do, before the modelling exercise, was hold the entire thing in my head at once.
 
---
 
## The diagram
 
The model uses BPMN 2.0, with two swim lanes representing the two functional roles involved: *Patrol Unit* (handling on-site detection and immediate contestation) and *Administrative Office* (handling documentation, notification, and all subsequent phases).

![Highway Code Sanctioning Process - BPMN 2.0](https://raw.githubusercontent.com/ale-saglia/insight/refs/heads/main/assets/process-sanctions-cds-en.bpmn.svg)

*[Download the source file](https://raw.githubusercontent.com/ale-saglia/insight/refs/heads/main/assets/process-sanctions-cds-en.bpmn)*

A few things worth noting in the model:
 
The process has two start events. This reflects a structural reality of Italian traffic enforcement: contestation can be immediate (on the spot) or deferred (by mail to the registered owner). These are not the same administrative path, even though they converge at the same subsequent steps.
 
The event-based gateway after notification handles three mutually exclusive waiting states: payment within 60 days (*Payment* timer event), a request for defensive writings (*Request for Defensive Writings* message event), and simple inaction (which triggers the 60-day deadline expiry). This was the hardest part of the model to get right, because in practice the three outcomes feel sequential rather than parallel. The gateway makes explicit that the process is actually suspended, waiting for one of three things to happen.
 
The loop from the gateway through defensive writings, appeal outcome, and back to the main flow reflects the real complexity of the appeals chain. In practice, this loop rarely completes more than twice. But it exists, and a model that ignores it is wrong.
 
---
 
## What modelling changed
 
When I finished the first draft of the diagram, I found three things I had not consciously known before, despite having executed the process hundreds of times.
 
The first was the double start event. I had always thought of immediate and deferred contestation as variations of the same thing. Modelling them made clear they are structurally different paths that happen to share most of their downstream steps. That distinction matters if you ever want to instrument the process or collect metrics separately.
 
The second was the event-based gateway. In practice, the 60-day wait and the possibility of a defensive request feel like sequential steps: you send the notice, you wait to see if they pay, and if they do not, you check for defensive writings. The model showed that these are actually concurrent waiting states, and that the administrative logic for handling them needs to account for both simultaneously. Several municipalities I later learned about had actually built their software to handle them sequentially, creating edge cases where a payment received on day 59 could be ignored because the system had already opened a defensive-writings sub-process.
 
The third was the annulment path. In practice, annulment in *autotutela* was rare enough that I barely thought about it as part of the process. In the model, it appears as a distinct end state that requires its own flow. Making it explicit forced me to think about what triggers it, who authorises it, and how it is recorded.
 
None of these were revelations. They were things I would have recognised immediately if someone had pointed them out. But I had not pointed them out to myself, because I had no tool that required me to be explicit about them.
 
---
 
## On governance work
 
The reason I find this worth writing about is not the BPMN diagram itself. It is what the exercise revealed about the relationship between tacit knowledge and formal structure.
 
People who work inside complex processes for years accumulate a detailed operational understanding of how things work. That understanding is real and valuable. It is also largely invisible: it lives in their heads, it is transmitted through observation and apprenticeship, and it is extremely difficult to examine critically from the inside.
 
Formal modelling is one tool for making that tacit knowledge visible. It does not replace operational experience. It surfaces it, names it, and creates a shared object that can be examined, critiqued, and improved.
 
This is, in a more structured form, the same thing I was trying to do when I built DESU: surface the compliance tracking logic that was living in spreadsheets and in people's heads, and give it a more explicit, queryable form.
 
The difference is that with DESU I was solving the problem with code before I understood the structure well enough to model it properly. The result worked, but it was brittle, difficult to extend, and dependent on my own understanding of what the firm actually needed.
 
If I were to rebuild it now, I would model the process first.