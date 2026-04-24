# Insight: Manifesto & Governance Principles

Technology is never neutral. The architecture of a system, the way data is processed, and the cadence of content delivery are all governance choices. 

*Insight* is built and maintained following a rigorous set of principles that bridge software engineering, editorial ethics, and interaction design. This document outlines the guidelines governing the project, aligning them with the core values of digital sovereignty, proportionality, and transparency.

## I. Editorial Principles (Content)

1. **Intentionality & Proportionality (Quality over Quantity)**
   The primary aim is clear thinking, not volume. The information ecosystem is already saturated with noise; every publication on *Insight* must have a specific intent and tangible value. Publication frequency is strictly subordinated to content relevance.

2. **Transparency & Human Accountability**
   Artificial Intelligence is utilized strictly as a writing and iteration aid, never as a generator of ideas or core arguments. Editorial responsibility ("Accountability") remains entirely human: all content is ideated, authored, and validated manually. This approach ensures a strict *Human-in-the-loop* oversight for every published asset.

## II. Engineering Principles (Code)

1. **Digital Sovereignty (Zero External Dependencies)**
   The infrastructure is designed to eliminate third-party points of failure and prevent vendor lock-in. The deliberate absence of external dependencies (e.g., SaaS search APIs or cloud-based asset generators) guarantees total control over the stack and the data. Even complex operations, such as generating Open Graph preview images, are executed locally during the build process.

2. **Engineering Proportionality (YAGNI)**
   System architecture must scale to actual needs, avoiding hypothetical hyper-growth scenarios that introduce unnecessary technical debt. For example, rather than implementing heavy full-text search libraries and JSON indexes, *Insight* utilizes pure DOM-based filtering. For the scale of this project, the math does not justify the complexity. The simplest solution is deliberately chosen as the most robust one.

3. **Security & Resiliency by Design**
   Deploying as a static site drastically reduces the attack surface. The complete absence of exposed databases, dynamic server-side rendering, and active middleware makes the infrastructure inherently secure and resilient by design.

## III. Design & UX Principles (Interface)

1. **Respect for the User & Privacy by Default**
   The interface is built to serve the user, not to track them. The "zero external dependencies" rule ensures there are no third-party scripts, profiling cookies, or hidden tracking pixels. Privacy is not a policy the user has to accept; it is the default, immutable state of the system.

2. **Accessibility as Performance**
   Ethical design is accessible design. By keeping the client payload strictly minimal and avoiding heavy JavaScript for core rendering, the site remains fast, responsive, and readable even on constrained connections or legacy devices.

3. **Frictionless Functionality**
   Interaction design must respect established web paradigms. For instance, filter states in the archive are persisted directly in the URL via `history.replaceState`. This makes custom filtered views instantly shareable and bookmarkable, respecting the user's time and choices without introducing backend complexity.