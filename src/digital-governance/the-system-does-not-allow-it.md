---
title: The System Does Not Allow It
created: 2026-07-10
modified: 2026-07-10
keywords: compliance by design, accountability, control and autonomy
excerpt: When a rule moves from a regulation to a system configuration, it stops asking to be obeyed and starts being executed. The same rule reads as a nudge to some and a wall to others, and the oldest excuse in the office becomes, for the first time, a checkable claim.
article_id: the-system-does-not-allow-it
---

A formal letter arrives at the centre of a multi-level organisation. One of the operating units states, in writing, that a shared administrative system does not allow it to complete a routine task. The phrasing is familiar to anyone who has ever stood at a public counter or waited on an internal ticket: the system does not allow it. The person is willing, the office is willing, the machine refuses. Nothing to be done.

The sentence has a long career precisely because it used to be unanswerable. When every office ran its own procedures on its own tools, blaming the software was a claim nobody could verify from outside. The rule lived in one place, the practice in another, and the gap between them belonged to whoever worked inside it.

This time the claim is checkable, and that is the entire story. Someone at the centre opens the same system the unit uses, follows the documented path, and finds the function. It has been available, and documented, since well before the letter was written. What the unit is missing is not a feature. It is the shortcut the system was designed to remove.

I have been circling this theme for a while without naming it. In an [earlier piece](/digital-governance/build-compliance-tool-before-i-know-compliance/) I described building tools to make compliance obligations visible before they became failures. In [another](/digital-governance/process-you-know-but-cannot-describe/) I argued that formal process modelling turns tacit operational knowledge into a shared object that can be examined and improved. This article is the third step of that argument. Once the obligations are visible and the process is modelled, the rule can be embedded in the system that executes the process. At that point something changes in kind, not just in degree. And the sentence at the counter changes meaning with it.

## From the regulation to the configuration

In operational terms, a rule written in a regulation works like a request. It asks to be read, understood, remembered and obeyed, and it relies on inspection after the fact to catch the cases where it was not. Between the rule and the behaviour sits a human being who must know the rule, recall it at the right moment, and choose to follow it. Every one of those steps can fail innocently, and every one of them can be made to fail on purpose.

A rule written into an enterprise system is a different kind of object. The approval chain that requires a second signature above a spending threshold, the mandatory field that will not let a contract exist without a responsible officer, the separation that prevents the person who orders from being the person who pays: none of these ask for anything. They execute. The distance between the rule and the behaviour collapses, because within the formal process the behaviour can occur only through the configured rule. The informal space outside the process does not vanish, and we will come to it, but it stops being the path of least resistance.

Lawrence Lessig made the general version of this point about the internet a quarter of a century ago: architecture regulates, and whoever writes the code is setting the rules of the space, whether or not anyone calls it regulation [1]. Enterprise systems are the institutional descendant of that insight. The research field that grew around it calls the approach compliance by design: control objectives derived from regulations and standards are propagated into process models, so that the process itself becomes the primary evidence of compliance rather than a report reconstructed afterwards [2]. The audit does not chase the transaction. The transaction carries its audit trail with it, because it could not have been recorded any other way.

The practical consequence is easy to state and easy to underestimate. When an organisation configures its administrative system, it is engaging in a form of internal rulemaking. The configuration workshop is where much of the real rulemaking happens. The people in that room, functional analysts, key users, a consultant from the vendor, are exercising a normative power that rarely appears in their job description and almost never receives the scrutiny that formal rulemaking would. This asymmetry, enormous practical effect and minimal procedural visibility, is the governance problem this article keeps returning to.

## The same rule, two readings

Here is the part I find genuinely elegant, and it emerged from watching how differently people react to the same constraint.

For someone working in good faith, a structured rule reads as a nudge. Strictly speaking, it is not one: in the sense Thaler and Sunstein gave the word, a nudge preserves freedom of choice, while a mandatory field or a blocked transaction removes options outright [3]. But a compliant operator experiences it in much the same way, as choice architecture that makes the correct path the easy path, guidance rather than coercion. The mandatory field is a reminder they did not have to keep in their head. The pre-built approval chain is a route they did not have to reconstruct from a circular. The default value is the answer that is right in the overwhelming majority of cases, offered before the question is asked. The system carries the regulation for them, and what it takes away, the effort of remembering the rule, was never something they wanted to carry.

For someone looking for a shortcut, the identical rule is enforcement. The purchase that used to bypass the contract register now cannot exist without one. The payment that used to be split to stay under a threshold now trips the aggregation check. The expense that used to be reclassified after the fact is locked to its category at entry. Nothing was announced, nobody was accused, and yet a category of informal practice quietly stopped being possible.

The rule did not change between these two readings. The reader did. And this is precisely the property that makes structural rules valuable in institutional settings: they are the only control that does not require anyone to presume bad faith. A spot inspection implies suspicion. An extra reporting obligation implies distrust of what was reported the first time. A structured process implies nothing at all. It simply makes the compliant path and the possible path the same path, and lets each person experience that fact according to their own intentions. The honest majority feels supported. The dishonest minority feels watched. The system, meanwhile, has said nothing about anyone.

The information systems literature has long recognised this ambivalence. The classic study by Sia and colleagues framed enterprise systems as a technology of power that can simultaneously empower employees, by giving them information and autonomy they never had, and tighten visibility over everything they do [4]. Both descriptions are accurate, and they are descriptions of the same configuration. Which one a given person offers you is often the most informative thing about them, provided the rule is well placed. A badly placed rule makes honest operators feel watched too, and that is a policy failure, not a character flaw. Placement, then, is the real design question.

## The grey zone, and why it should be designed rather than avoided

Between the gentle default and the hard block there is a middle register, and it is where the most interesting design decisions live.

Consider the warning that can be overridden. The system flags that a payment is close to a threshold, or that a supplier already holds an unusually high share of recent orders, and it lets the operator proceed. Pure nudge: information at the moment of choice, freedom intact. Now consider the same warning with one addition: proceeding requires the operator to record a reason, which is stored with the transaction. This is no longer quite a nudge, and not yet a wall. It is enforcement of accountability rather than enforcement of the rule itself.

I find this pattern underused and undervalued, perhaps because it sits awkwardly between the two vocabularies. In legal terms it is simply the duty to state reasons, transplanted from the administrative act into the transaction record. Public law has always known that the obligation to motivate a decision disciplines the decision better than most prohibitions, because a reason must be written by someone, addressed to someone, and defensible later. Translated into system design, the recorded override does three things at once. It preserves the flexibility that rigid rules destroy, because the exceptional case can still go through. It converts every exception into data, so the centre can see which rules are overridden often and ask whether the rule or the practice is wrong. And it changes the private calculation of the person acting in bad faith more effectively than a block would, because a block invites a workaround while a recorded reason invites a signature.

A well-designed rule set is therefore not a wall with a few doors. It is a gradient: defaults where error is the risk, recorded overrides where judgement is legitimate, hard blocks only where the law itself admits no exception. Getting a rule's position on that gradient wrong, in either direction, is a policy failure, not a technical one.

## Standardisation is what makes the levels governable

The argument so far works for a single organisation. It becomes considerably stronger in multi-level structures: a holding company and its subsidiaries, a head office and its branches, a central entity and a network of semi-autonomous units. In these structures the centre typically carries responsibility for the whole, consolidated accounts, group-level compliance, answerability to an external authority, while the units retain operational autonomy and, with it, the ability to develop local practices that the centre cannot see.

A shared system with structured rules changes the geometry. When every unit runs the same process on the same platform, the units become comparable in a way that no reporting obligation ever achieved. The same transaction type looks the same everywhere. A deviation in one unit is visible as a deviation, not as a local custom. Consolidation stops being an exercise in translation. Audit stops depending on each unit's willingness to explain itself. Benchmarking, the simple question of why the same process costs three times as much in one unit as in another, becomes possible for the first time, because for the first time it is the same process.

Organisational sociology has a name for the deliberate production of this similarity. DiMaggio and Powell called it coercive isomorphism: the pressure that a resource-controlling centre exerts on dependent organisations, making them structurally alike and, as a consequence, legible to it [5]. The term was coined as a diagnosis, not a recommendation, and the critical edge should be kept in view. Uniformity has costs, and some local variation encodes genuine local knowledge rather than local convenience. But in structures where the centre is legally accountable for the conduct of the units, legibility is not a managerial vanity. It is the precondition for the accountability actually functioning. An accountability that cannot see what it answers for is a fiction maintained at the centre's expense.

There is a real tension here, and I have written about its other face before. In [a piece on single sources of truth](/digital-governance/single-source-truth-no-tech-problem/) I argued that local practices are not always duplication to be eliminated: some variation is convenience, and some encodes genuine local knowledge. A shared system should absorb the first and leave breathing room for the second. Where exactly that line runs, and why it cannot simply be read off the vendor's reference model, deserves an article of its own. Here it marks the honest limit of the standardisation case.

The same logic extends beyond financial resources. A standardised process protects personal data for the same reason it protects public money: the improvised shortcut, the spreadsheet of records exported and emailed because the official channel was slow, disappears when the system carries the data through the authorised path by default. Data protection by design and sound financial control turn out to be the same architectural habit applied to different assets. The shortcut economy does not distinguish between the assets it endangers, and neither should the architecture that shuts it down.

## The system becomes the scapegoat

Now the counter-argument, because there is one, and it does not take the form you might expect.

The textbook objection to structured rules is rigidity: configure the process badly and the system enforces the error at scale, with a diligence no human bureaucracy could match. This is true, and the gradient described above is part of the answer. A structured system without a functioning, documented path for requesting exceptions and evolutions is not governance. It is concrete.

But the failure mode I find more instructive is subtler, and it brings us back to the letter this article opened with. When a system becomes the instrument through which rules are enforced, it also becomes the perfect scapegoat for anyone who preferred the old arrangements. Resistance to the rule can be laundered as a technical complaint. "The system does not allow it" is a claim that costs nothing to make, sounds objective, carries no admission of unwillingness, and shifts the burden of proof onto the centre. If the claim goes unanswered, silence reads as admission, and responsibility for every delay migrates from the unit that will not adopt the process to the platform that supposedly cannot support it.

Steven Alter's theory of workarounds describes the underlying dynamic well: when participants perceive an obstacle between them and their goals, they weigh the costs and benefits of routing around it, and the formal system's constraints are just one input into that calculation [6]. What the theory implies, and what practice confirms, is that contesting the system is itself a workaround. It is cheaper than changing how you work and safer than openly refusing to. It also scales: a claim made in a formal letter obliges the centre to respond formally, and every week the response takes is a week of the old practice.

The governance response is not to argue louder. It is to classify. Every claimed gap belongs to one of a small number of categories: the function exists; the function exists but is unknown or locally misconfigured; the function exists through a different path than the one the unit expects; the request is a genuine evolution, approved or under evaluation; the request was never formally submitted through the agreed channel; or the request is, on examination, an attempt to preserve a practice the model deliberately excludes. An organisation that maintains this register, and answers every formal claim with a formal, point-by-point classification, converts a war of assertions into an administrative record. The units that were negotiating in bad faith lose their instrument, because an unfounded claim now produces a documented refutation instead of a delay. The units with genuine needs, and there are always some, finally get an answer with a date on it. And the centre protects itself, because the register is also the proof of who was asked to do what, and when.

This is the quieter lesson of the whole exercise. Embedding rules in a system does not end the political work. It relocates it, from enforcing the rule to defending the record of what the system actually does. The centre that builds the platform and neglects the register has done the expensive half of the job and skipped the half that decides whether the expensive half survives.

## Rules deserve version control

One last consequence follows from taking the argument seriously, and it points back at the centre rather than the units.

If the configuration is where the rules live, then the configuration is a normative text, and it should be treated with the care normative texts receive. A change to an approval threshold or a mandatory field is not maintenance. It is an amendment. It ought to be attributable to someone with the authority to make it, reviewed before it takes effect, documented in a form that others can read, and reversible when it turns out to be wrong.

I learned the small version of this lesson in my own infrastructure, where [moving every service definition into a versioned repository](/infrastructure/zero-to-homelab/gitops-and-secrets/) turned invisible, drifting configurations into a legible history of deliberate changes. The institutional version is the same discipline at a different scale. An organisation that can answer the question "who changed this rule, when, and why" about its own system holds the complete chain from the regulation to the behaviour: the law, the control objective derived from it, the configuration that implements the objective, and the log of how that configuration evolved. An organisation that cannot answer it has built an enforcement machine governed by folklore, and will discover the cost the first time an enforced rule turns out to be an implemented mistake and nobody can say where it came from.

The units are accountable through the system. The centre is accountable for it. Neither accountability works without a record.

## Closing

A rule on paper asks to be obeyed and waits to be broken. A rule in the system executes, and is experienced as help by those who wanted to comply and as a wall by those who did not. Between the two runs a gradient of defaults, recorded overrides and hard blocks, and placing each rule correctly on that gradient is policy work wearing technical clothes.

"The system does not allow it" used to be the end of a conversation. In a well-governed structure it is the beginning of one, because the claim is now checkable, classifiable and answerable, and the answer leaves a record.

The configuration is the policy. Whoever writes it is legislating, and should be chosen, and held to account, accordingly.

## Sources

All sources accessed 10 July 2026.

1. Lawrence Lessig, "Code Is Law: On Liberty in Cyberspace", Harvard Magazine, January 2000. https://www.harvardmagazine.com/2000/01/code-is-law-html
2. Shazia Sadiq, Guido Governatori, Kioumars Namiri, "Modeling Control Objectives for Business Process Compliance", BPM 2007, Lecture Notes in Computer Science vol. 4714, Springer. https://link.springer.com/chapter/10.1007/978-3-540-75183-0_12
3. Richard H. Thaler, Cass R. Sunstein, *Nudge: Improving Decisions About Health, Wealth, and Happiness*, Yale University Press, 2008. https://yalebooks.yale.edu/book/9780300262285/nudge/
4. Siew Kien Sia, May Tang, Christina Soh, Wai Fong Boh, "Enterprise Resource Planning (ERP) Systems as a Technology of Power: Empowerment or Panoptic Control?", The DATA BASE for Advances in Information Systems, 33(1), 2002. https://dl.acm.org/doi/10.1145/504350.504356
5. Paul J. DiMaggio, Walter W. Powell, "The Iron Cage Revisited: Institutional Isomorphism and Collective Rationality in Organizational Fields", American Sociological Review, 48(2), 1983. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1504516
6. Steven Alter, "Theory of Workarounds", Communications of the Association for Information Systems, 34(55), 2014. https://doi.org/10.17705/1CAIS.03455
