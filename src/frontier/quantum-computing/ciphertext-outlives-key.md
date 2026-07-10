---
title: The Ciphertext Outlives Its Key
created: 2026-04-24
modified: 2026-07-10
keywords: digital sovereignty, accountability, operational resilience
excerpt: Nine years ago I asked whether quantum computing would eventually kill Bitcoin.
  The same question, asked today about a national genetic database, has none of the
  qualities that made the original speculative.
article_id: ciphertext-outlives-key
---

Nine years ago, on LinkedIn, I [published a short piece](https://www.linkedin.com/pulse/feynman-uccider%C3%A0-i-bitcoin-alessandro-saglia/) asking whether quantum computing would eventually kill Bitcoin. The framing was speculative on both ends. The cryptographic break was decades away. The asset at risk was itself a bet on a cryptographic abstraction. It was a thought experiment about a possible future.

The same question, asked today about a national genetic database, has none of those qualities.

The cryptographic break is no longer something long-lived systems can safely treat as comfortably distant. The asset at risk is not a speculative ledger but the genomic identity of a population. And security agencies already treat the collection of encrypted material for later decryption as a present risk rather than a hypothetical future technique [1].

---

## A packet on a wire

Somewhere on a transatlantic fibre link, a packet leaves a national biobank and travels to a research collaborator abroad. It contains thousands of sequenced genomes, with consent forms, identifiers, and metadata. It is encrypted. The key exchange relies on elliptic-curve cryptography, which is the current standard for protecting data in transit. By every reasonable measure today, the packet is safe.

It may also be copied.

Not necessarily by the recipient, or by the carrier, or by anyone the sender would recognise as an adversary. The copy may be made by a passive observer somewhere along the route, sitting on an interception point and writing ciphertext to long-term storage. The copy does not need to be readable now. Storage is cheap, and the observer can afford to wait.

This is the tactic the security community calls *Harvest Now, Decrypt Later*. The first half must be treated as a present threat. The second half is waiting for an instrument that does not yet exist [1].

---

## The arithmetic that does not work

There is a simple inequality that frames the entire problem, first articulated by cryptographer Michele Mosca. It asks three questions. How long does this data need to remain confidential? How long will the migration to quantum-resistant cryptography take? How long until a cryptographically relevant quantum computer exists? [2]

If the first two added together are greater than the third, the data is already exposed to the risk that the ciphertext will outlive the cryptography protecting it. The point is not that decryption is possible today. It is that migration beginning after the inequality has crossed cannot protect every copy already collected.

For most categories of data, the arithmetic is uncomfortable but manageable. Financial transactions have confidentiality horizons measured in years. Communications metadata in months. Even classified material, though sensitive, usually has a defined downgrade path.

A genomic sequence has none of these properties. It is confidential for as long as its subject is alive. Unlike a password or a credit card number, it cannot be rotated or revoked. It also implicates people who never consented to its disclosure: full siblings share roughly half of their inherited DNA, as do parents and children, while more distant relatives share progressively less but still measurably so. Genomic privacy is therefore relational as well as individual [3]. A single sequence, broken thirty years from now, may retroactively expose a family that did not exist when the sequence was collected.

Migration timelines for complex, regulated infrastructure are measured in years rather than release cycles. The European coordinated roadmap calls for critical infrastructures to transition as soon as possible, no later than the end of 2030, and for other systems to complete the transition by the end of 2035 [4]. Devices and platforms governed by certification cycles may move more slowly still.

The third variable is the contested one. No reliable public forecast can identify the date of a cryptographically relevant quantum computer. What the research does show is that cryptanalytic resource estimates can improve substantially, while fault-tolerant quantum computing still requires capabilities far beyond current machines [5][6]. That uncertainty is not a reason to choose a reassuring date. For genomic data, a planning horizon extending into the 2030s or 2040s is already short enough to make the inequality operationally relevant.

---

## What HNDL actually requires

The most common misunderstanding about HNDL is that it is only a future threat. It is better understood as a present collection strategy whose consequences are deferred [1].

To execute the harvest, an adversary does not need to compromise the database. They do not need to deploy malware on a research endpoint, phish an administrator, or exploit a vulnerability in a sequencing platform. None of the conventional detection signals need fire. There may be no incident visible to the data holder.

What they need is a position on the network path between two endpoints, and the storage to write ciphertext to disk at scale. Both are within the capabilities of sophisticated actors. The missing component is a machine able to run the required cryptanalysis at useful scale.

Whatever one's view of specific timelines, agencies and standards bodies now treat the probability of such a machine arriving within the lifetime of long-lived encrypted data as sufficient to justify migration today [1][4].

Where vulnerable ciphertext has already been intercepted and retained, no later migration can retroactively protect that copy. Migration can stop the accumulation of new exposure. It cannot erase an adversary's existing archive.

This is the most difficult thing to communicate to non-technical stakeholders. When the migration to post-quantum cryptography completes, it will not make the historical problem disappear. It will stop adding to it.

---

## The cryptography is the easy part

The instinct, facing a problem framed this way, is to focus on algorithms. Which post-quantum schemes are ready? Which has NIST standardised? Which constructions remain robust under implementation constraints? These are important questions, and the first standardisation decisions have now been made: ML-KEM for key encapsulation, ML-DSA and SLH-DSA for signatures, with implementation and deployment work still continuing [7][8][9].

The algorithms are the easy part. The difficult work begins the moment they need to be deployed.

Deploying post-quantum cryptography at the scale of a national or supranational data infrastructure requires, first, knowing where cryptography currently lives. Not just in the obvious places, TLS terminators, application-level encryption, certificate authorities, but in firmware on instruments, in hardcoded libraries inside platforms, in the authentication modules of interoperability layers, in legacy middleware that nobody has touched in five years because it works.

Most organisations do not have this inventory. In a fragmented infrastructure of national systems, institutional procurement, and international vendors, no single actor owns the map. Migration guidance therefore begins with cryptographic discovery and inventory: locating vulnerable public-key algorithms, documenting dependencies, and identifying the systems that must change [1][10]. The inventory itself is a governance deliverable before it is a technical one. It requires agreement on scope, on ownership, on what counts as a cryptographic asset, and on who updates the catalogue when something changes.

Once the inventory exists, the second question is who controls the migration path for each item. Some assets are under the direct control of the operator. Others depend on a vendor releasing a firmware update. Others depend on a standards body publishing a new specification. Others depend on a cloud provider rolling out support in a managed service. The operator's ability to migrate is, for any given asset, equal to the slowest dependency in that chain.

This is why *crypto-agility*, the capacity to replace cryptographic algorithms and implementations without redesigning every dependent system, has emerged as a central architectural concern [11]. But crypto-agility is not a property of an algorithm. It is a property of how infrastructure is designed, procured, and operated. It requires abstraction layers that many existing systems do not have, contract terms that many vendor relationships do not include, and operational discipline that many teams are not organised to deliver.

In this sense, the quantum migration inherits a familiar pattern. The technical decision, choosing ML-KEM, is a small part of the work. The organisational decision, rebuilding how cryptographic dependencies are managed, is where the difficulty lives.

---

## The jurisdictional complication

For European data, there is an additional layer that makes the arithmetic worse, and for genomic data the layer is particularly thick.

Many of the largest aggregations of human genetic data are held under non-European jurisdictions, whether by sovereign biobanks abroad, by consumer genetic services, or by research consortia hosted on infrastructure provided by non-European hyperscalers. The compromise that has allowed European data to coexist with such arrangements has been *customer-managed encryption*: the cloud provider operates the infrastructure, but the customer controls the keys. When a foreign authority issues an extraterritorial request for data, the provider can comply in the legal sense, by producing the ciphertext, while the customer's keys remain out of reach. The data is technically disclosed, but unreadable.

This compromise depends entirely on the classical cryptography assumption. It assumes that ciphertext produced by today's algorithms, even if handed to a foreign authority, remains computationally useless. That assumption is what allows the arrangement to be described as privacy-preserving.

When the assumption expires, so does the compromise. Ciphertext collected under an extraterritorial production order today may become readable material tomorrow, in the same way that ciphertext intercepted on a fibre link may. The legal instrument is different, the adversary is different, but the underlying exposure is the same: data obscured rather than permanently protected, waiting for an instrument to arrive.

For genetic data the consequences are categorical. A genomic dataset disclosed in fifteen years is not a historical curiosity. It is operational information about the people in it, about their living relatives, and potentially about populations that may have been the subject of targeted study without ever being told. Genetic data does not age out of relevance [3].

The European regulatory architecture has begun to encode this shift, but not yet in a way that forces action on the timeline the arithmetic demands. The debates around cloud certification, supply-chain assurance, and operational resilience are converging on the right questions. They are not yet converging fast enough.

---

## What can actually be done

There is no version of this problem where the right response is to wait for certainty. The migration path is long, while the exposure concerns data whose confidentiality horizon may span decades.

The useful posture, for any organisation holding long-lived genetic or biometric data, involves three things, none of which are primarily about cryptography.

The first is the inventory. Not an audit for compliance, but an operational map of where cryptographic primitives are used, what their replacement paths look like, and who owns each migration. This is slow work, and it does not produce visible deliverables until it is complete. It is also the prerequisite for everything else [1][10].

The second is a procurement posture. New contracts for infrastructure, instruments, and cloud services should require crypto-agility as a functional requirement, not an aspirational one. Specifically: support for hybrid classical-plus-post-quantum schemes during the transition, defined algorithm replacement pathways, and clear vendor commitments on migration timelines. The cost of adding these requirements now is modest compared with discovering later that a critical platform has no supported migration path.

The third is a realistic view of what the migration will not fix. Ciphertext already intercepted and retained is not protected by any future cryptographic upgrade. Other historical copies, in backups, research archives, or replicated systems, require a separate assessment: whether they can be re-encrypted, whether their storage and key-management model can be changed, and what residual exposure must be accepted. These are not questions with clean answers, but they need to be asked before the arrival of the capability that makes the archive readable.

---

## Closing

Nine years ago I asked whether Feynman would kill Bitcoin. The honest answer was probably yes, eventually, but the stakes were containable. A speculative asset can lose its value. A market can be repriced. A protocol can be forked. The harm, if it ever materialised, would be financial and bounded.

The question I am asking now is whether the same instrument, on the same broad technological trajectory, could expose the genomic identity of populations that have already given their samples to systems built on cryptographic assumptions that will not hold indefinitely. The answer is that the risk is credible enough to govern now. The stakes are not containable in the same way. A genome cannot be repriced or reissued. The relatives implicated by it cannot be opted out retroactively. The harm, if it materialises, is not merely financial.

The standard framing of the quantum threat is that a new class of computer will break today's encryption. This is true, but it puts the emphasis in the wrong place. The more accurate framing is that the useful life of our cryptography may be shorter than the useful life of our data, and that collection can exploit that gap before decryption is possible. The quantum computer, if and when it arrives, will be the instrument that converts an existing archive of vulnerable ciphertext into an archive of plaintext.

The encryption has an expiration date. The data does not.

## Sources

All sources accessed 10 July 2026.

1. CISA, NSA and NIST, "Quantum-Readiness: Migration to Post-Quantum Cryptography", August 2023. https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography
2. Michele Mosca, "Cybersecurity in an Era with Quantum Computers: Will We Be Ready?", IEEE Security & Privacy, 16(5), 2018. https://doi.org/10.1109/MSP.2018.3761723
3. Zhiyu Wan, James W. Hazel, Ellen Wright Clayton, Yevgeniy Vorobeychik and Murat Kantarcioglu, "Sociotechnical safeguards for genomic data privacy", Nature Reviews Genetics, 23, 2022. https://doi.org/10.1038/s41576-022-00455-y
4. NIS Cooperation Group, "A Coordinated Implementation Roadmap for the Transition to Post-Quantum Cryptography", European Commission, June 2025. https://digital-strategy.ec.europa.eu/en/library/coordinated-implementation-roadmap-transition-post-quantum-cryptography
5. Craig Gidney and Martin Ekerå, "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits", Quantum, 5, 2021. https://doi.org/10.22331/q-2021-04-15-433
6. Travis L. Scholten, Carl J. Williams, Dustin Moody, Michele Mosca, William Hurley, William J. Zeng, Matthias Troyer and Jay M. Gambetta, "Assessing the Benefits and Risks of Quantum Computers", 2024. https://arxiv.org/abs/2401.16317
7. National Institute of Standards and Technology, FIPS 203, "Module-Lattice-Based Key-Encapsulation Mechanism Standard", August 2024. https://csrc.nist.gov/pubs/fips/203/final
8. National Institute of Standards and Technology, FIPS 204, "Module-Lattice-Based Digital Signature Standard", August 2024. https://csrc.nist.gov/pubs/fips/204/final
9. National Institute of Standards and Technology, FIPS 205, "Stateless Hash-Based Digital Signature Standard", August 2024. https://csrc.nist.gov/pubs/fips/205/final
10. National Cybersecurity Center of Excellence, "Migration to Post-Quantum Cryptography". https://www.nccoe.nist.gov/projects/building-blocks/post-quantum-cryptography
11. National Institute of Standards and Technology, "Considerations for Achieving Crypto Agility: Strategies and Practices", Cybersecurity White Paper, December 2024. https://csrc.nist.gov/pubs/cswp/39/considerations-for-achieving-crypto-agility/final
