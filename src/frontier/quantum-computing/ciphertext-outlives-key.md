---
title: The Ciphertext Outlives Its Key
created: 2026-04-24
keywords: post-quantum cryptography, genetic databases, HNDL, crypto-agility, data
  sovereignty, biobanks
excerpt: Nine years ago I asked whether quantum computing would eventually kill Bitcoin.
  The same question, asked today about a national genetic database, has none of the
  qualities that made the original speculative.
article_id: ciphertext-outlives-key
---

Nine years ago, on LinkedIn, I [published a short piece](https://www.linkedin.com/pulse/feynman-uccider%C3%A0-i-bitcoin-alessandro-saglia/) asking whether quantum computing would eventually kill Bitcoin. The framing was speculative on both ends. The cryptographic break was decades away. The asset at risk was itself a bet on a cryptographic abstraction. It was a thought experiment about a possible future.

The same question, asked today about a national genetic database, has none of those qualities.

The cryptographic break is no longer comfortably decades away. The asset at risk is not a speculative ledger but the genomic identity of a population. And the harvesting of the encrypted material that will eventually be broken is not hypothetical: it is happening now, on the wires, while the data is being generated.

---

## A packet on a wire

Somewhere on a transatlantic fibre link, a packet leaves a national biobank and travels to a research collaborator abroad. It contains thousands of sequenced genomes, with consent forms, identifiers, and metadata. It is encrypted. The key exchange relies on elliptic-curve cryptography, which is the current standard for protecting data in transit. By every reasonable measure today, the packet is safe.

It will also be copied.

Not necessarily by the recipient, or by the carrier, or by anyone the sender would recognise as an adversary. The copy will be made by a passive observer somewhere along the route, sitting on an interception point and writing ciphertext to long-term storage. The copy does not need to be readable now. Storage is cheap, and the observer can afford to wait.

This is the tactic the security community calls *Harvest Now, Decrypt Later*. The first half is happening today. The second half is waiting for an instrument that does not yet exist.

---

## The arithmetic that does not work

There is a simple inequality that frames the entire problem, first articulated by cryptographer Michele Mosca. It asks three questions. How long does this data need to remain confidential? How long will the migration to quantum-resistant cryptography take? How long until a cryptographically relevant quantum computer exists?

If the first two added together are greater than the third, the data is already compromised. Not metaphorically. The ciphertext will outlive the cryptography that protects it.

For most categories of data, the arithmetic is uncomfortable but manageable. Financial transactions have confidentiality horizons measured in years. Communications metadata in months. Even classified material, though sensitive, usually has a defined downgrade path.

A genomic sequence has none of these properties. It is confidential for as long as its subject is alive. Unlike a password or a credit card number, it cannot be rotated. It cannot be revoked. It also implicates people who never consented to its disclosure: full siblings share roughly half of it, parents and children share roughly half of it, more distant relatives share progressively less but still measurably so. A single sequence, broken thirty years from now, retroactively exposes a family that may not have existed at the time the sequence was collected.

Migration timelines for complex, regulated infrastructure are measured in a decade. The European coordinated roadmap sets a 2030 target for critical systems and a 2035 endpoint for deprecating vulnerable algorithms. Devices and platforms governed by certification cycles move even more slowly.

The third variable is the contested one. Estimates for a cryptographically relevant quantum computer have compressed significantly over the past two years, driven by hardware progress that has repeatedly outperformed conservative projections. Published research on quantum error correction, reductions in the qubit requirements for breaking RSA and elliptic-curve cryptography, and demonstrations of below-threshold logical qubits have all moved faster than the cryptographic community expected. Whether the date is 2030 or 2040 is, for genomic data, immaterial. Either way, the inequality does not balance.

---

## What HNDL actually requires

The most common misunderstanding about HNDL is that it is a future threat. It is not. It is a present operation whose consequences are deferred.

To execute the harvest, an adversary does not need to compromise the database. They do not need to deploy malware on a research endpoint, phish an administrator, or exploit a vulnerability in a sequencing platform. None of the conventional detection signals fire. There is no incident to respond to.

What they need is a position on the network path between two endpoints, and the storage to write ciphertext to disk at scale. Both have been technically and economically accessible to state-level actors for more than a decade. The only thing missing, until recently, was confidence that the future half of the operation, the decryption, would eventually become feasible.

That confidence now exists. Whatever one's view of specific timelines, the probability that the instrument will arrive within the useful lifetime of today's encrypted traffic is no longer negligible.

The consequence is that the present exposure is already sunk. No cryptographic migration undertaken today can protect data that has already crossed a wire in a form that will be readable in fifteen years. That data is, for practical purposes, copied.

This is the most difficult thing to communicate to non-technical stakeholders. When the migration to post-quantum cryptography completes, it will not make the problem go away. It will stop adding to it.

---

## The cryptography is the easy part

The instinct, facing a problem framed this way, is to focus on algorithms. Which post-quantum schemes are ready? Which has NIST standardised? Which lattice constructions are robust against side-channel attacks? These are important questions, and they have largely been answered. ML-KEM for key encapsulation, ML-DSA and SLH-DSA for signatures, with ongoing work on alternatives.

The algorithms are the easy part. The difficult work begins the moment they need to be deployed.

Deploying post-quantum cryptography at the scale of a national or supranational data infrastructure requires, first, knowing where cryptography currently lives. Not just in the obvious places, TLS terminators, application-level encryption, certificate authorities, but in firmware on instruments, in hardcoded libraries inside platforms, in the authentication modules of interoperability layers, in legacy middleware that nobody has touched in five years because it works.

Most organisations do not have this inventory. In a fragmented infrastructure of national systems, institutional procurement, and international vendors, no single actor owns the map. The inventory itself is a governance deliverable before it is a technical one: it requires agreement on scope, on ownership, on what counts as a cryptographic asset, and on who updates the catalogue when something changes.

Once the inventory exists, the second question is who controls the migration path for each item. Some assets are under the direct control of the operator. Others depend on a vendor releasing a firmware update. Others depend on a standards body publishing a new specification. Others depend on a cloud provider rolling out support in a managed service. The operator's ability to migrate is, for any given asset, equal to the slowest dependency in that chain.

This is why *crypto-agility*, the capacity to swap cryptographic primitives without redesigning the systems that use them, has emerged as the central architectural concern. But crypto-agility is not a property of an algorithm. It is a property of how infrastructure is designed, procured, and operated. It requires abstraction layers that most existing systems do not have, contract terms that most existing vendor relationships do not include, and operational discipline that most existing teams are not organised to deliver.

In this sense, the quantum migration inherits a familiar pattern. The technical decision, choosing ML-KEM, is a small part of the work. The organisational decision, rebuilding how cryptographic dependencies are managed, is where the difficulty lives.

---

## The jurisdictional complication

For European data, there is an additional layer that makes the arithmetic worse, and for genomic data the layer is particularly thick.

Many of the largest aggregations of human genetic data are held under non-European jurisdictions, whether by sovereign biobanks abroad, by consumer genetic services, or by research consortia hosted on infrastructure provided by non-European hyperscalers. The compromise that has allowed European data to coexist with such arrangements has been *customer-managed encryption*: the cloud provider operates the infrastructure, but the customer controls the keys. When a foreign authority issues an extraterritorial request for data, the provider can comply in the legal sense, by producing the ciphertext, while the customer's keys remain out of reach. The data is technically disclosed, but unreadable.

This compromise depends entirely on the classical cryptography assumption. It assumes that ciphertext produced by today's algorithms, even if handed to a foreign authority, remains computationally useless. That assumption is what allows the arrangement to be described as privacy-preserving.

When the assumption expires, so does the compromise. Ciphertext collected under an extraterritorial production order today becomes readable material tomorrow, in the same way that ciphertext intercepted on a fibre link does. The legal instrument is different, the adversary is different, but the underlying exposure is the same: data obscured rather than protected, waiting for an instrument to arrive.

For genetic data the consequences are categorical. A genomic dataset disclosed in fifteen years is not a historical curiosity. It is operational intelligence about the people in it, and about their living relatives, and about populations that may have been the subject of targeted study without ever being told. Genetic data does not age out of relevance.

The European regulatory architecture has begun to encode this shift, but not yet in a way that forces action on the timeline the arithmetic demands. The debates around cloud certification, supply-chain assurance, and operational resilience are converging on the right questions. They are not yet converging fast enough.

---

## What can actually be done

There is no version of this problem where the right response is to wait and see. The traffic is being collected now, and the migration path is long.

The useful posture, for any organisation holding long-lived genetic or biometric data, involves three things, none of which are primarily about cryptography.

The first is the inventory. Not an audit for compliance, but an operational map of where cryptographic primitives are used, what their replacement paths look like, and who owns each migration. This is slow work, and it does not produce visible deliverables until it is complete. It is also the prerequisite for everything else.

The second is a procurement posture. New contracts for infrastructure, instruments, and cloud services should require crypto-agility as a functional requirement, not an aspirational one. Specifically: support for hybrid classical-plus-post-quantum schemes during the transition, defined algorithm replacement pathways, and clear vendor commitments on migration timelines. The cost of adding these requirements now is trivial compared to the cost of not having them in five years.

The third is a realistic view of what the migration will not fix. The data already in transit, already in backups, already in long-term research archives, is not protected by any future cryptographic upgrade. It requires a separate category of decision: whether to re-encrypt, whether to move to cryptographically different storage, whether to accept the exposure and focus mitigation on the data that can still be saved. These are not questions that have good answers, but they are questions that need to be asked, because the alternative is to discover the answer when the key arrives.

---

## Closing

Nine years ago I asked whether Feynman would kill Bitcoin. The honest answer was probably yes, eventually, but the stakes were containable. A speculative asset can lose its value. A market can be repriced. A protocol can be forked. The harm, if it ever materialised, would be financial and bounded.

The question I am asking now is whether the same instrument, on the same timeline, will expose the genomic identity of populations that have already given their samples to systems built on cryptographic assumptions that have not aged well. The answer is also yes. The stakes are not containable in the same way. A genome cannot be repriced or reissued. The relatives implicated by it cannot be opted out retroactively. The harm, when it materialises, is not financial.

The standard framing of the quantum threat is that a new class of computer will break today's encryption. This is true, but it puts the emphasis in the wrong place. The more accurate framing is that the useful life of our cryptography is shorter than the useful life of our data, and that the gap is being exploited in the present tense. The quantum computer, when it arrives, will be the instrument that converts an existing archive of ciphertext into an existing archive of plaintext. The harvesting is happening now.

The encryption has an expiration date. The data does not.
