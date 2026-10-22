# Non-Functional Requirements (NFR) Checklist

Reference for judging whether non-functional requirements in a PRD or spec are quantified. Seven categories are the canonical set.

## Definition: "Quantified"

An NFR is **quantified** when a third party can decide pass/fail from the text alone: a number with a unit, or a named standard with its version and level.

### Four Levels

Use these levels as the vocabulary for judging an NFR statement.

| Level | Name | Meaning | Example |
|:------|:-----|:--------|:--------|
| 0 | Not stated | The category is not mentioned | (no performance requirement) |
| 1 | Mention only | Named, but no target value | "Must be fast" |
| 2 | Target value | Number with unit, standard with version/level, or a **checkable binary condition** (see below) | "p95 response time under 500 ms"; "does not depend on an external network" |
| 3 | Target + condition + verification | Level 2 plus the load/environment conditions and how it is verified (measured, tested, or checked in CI) | "p95 under 500 ms at 1,000 concurrent users, verified by load test on staging" |

Level 2 means the target is written in a form a third party can judge (the definition above).

**Checkable binary condition**: a statement a third party can answer yes/no from the text and an inspection, with no number needed. Typical forms: an enumerated list of allowed or forbidden items, a state-transition table, or an explicit prohibition. Examples (Level 2): "does not depend on an external network" (Reliability), "running the same input twice gives the same output" (Reliability, reproducibility), "only the listed 5 libraries may be imported" (Maintainability). A bare adjective ("minimal dependencies", "works offline well") stays Level 1.

**Compatibility with OS names only**: naming just the OS or runner (e.g., "Linux and macOS", "ubuntu-latest") is **Level 2**: the supported set is a closed, checkable list. Adding versions or a support window (e.g., "Ubuntu 22.04 and 24.04", "latest 2 majors") is not a different level; it is an element of Level 3 only when it comes together with a stated verification (condition + verification, e.g., "verified by CI on each"). Versions without verification stay Level 2. An OS name **plus continuous verification in CI, with no version** (e.g., "Linux and macOS, verified by CI on every merge") is **Level 3**.

Level 3 goes further: conditions and the verification method are given, so the result can be verified reproducibly. Level 2 targets (e.g., a percentile without a load condition) are judgeable but may be measured differently by different people; that gap is what Level 3 closes.

### Mapping to Risk Tiers (for #9)

Guideline only: Level 0 maps to High risk, Level 1 to Medium, Level 2 or higher to Low. How the seven categories are aggregated into a single High/Medium/Low is decided on the consumer side (issue #9), not here.

## Mapping Requirements to the Seven Categories

Assign each requirement to exactly one category with this table. This table is not an exhaustive list of requirement types; it covers the boundary cases that were hard to place. When a statement fits two rows, the **upper row takes priority; do not reorder the rows**.

| Requirement wording | Category |
|:--------------------|:---------|
| Portability: supported OS / runtime / platform / data format | Compatibility |
| Offline reproduction, no dependence on an external network, deterministic result | Reliability |
| Restricting dependencies (allowed/forbidden libraries, no external packages) | Maintainability |

A requirement that fits no category (e.g., "state what PASS means", a wording or documentation duty) is **out of scope for V6**: it is judged as an ordinary requirement under `ambiguity_criteria.md` Section 1, not as an NFR.

## Ranges as Guidance

The ranges below are rough starting points, not requirements. All numbers in this document, including those in examples, are illustrative and not recommended values; choose targets from the product's actual context.

## Categories

These seven categories are a grouping for requirement writing. They relate loosely to the product quality model of ISO/IEC 25010 (2023 edition); names are not guaranteed to match its characteristic names one-to-one.

### 1. Performance

- **What to state**: response time (percentile), throughput, resource usage, batch duration
- **Guidance range** (illustrative): interactive operations: hundreds of ms to a few seconds at p95; batch: minutes to hours depending on volume

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "The system responds quickly" | 1 |
| Bad | "Search is fast" (no target) | 1 |
| Good | "Search returns within 2 seconds (p95)" | 2 |
| Good | "Search returns within 2 seconds (p95) with 10M records and 100 concurrent users, verified by load test" | 3 |

### 2. Security

- **What to state**: authentication/authorization, encryption (in transit / at rest), vulnerability classes covered, audit logging, data retention
- **Standards**: OWASP Top 10 (2025 edition) as a vulnerability-class baseline
- **Guidance range**: the standard and edition to comply with; encryption protocol minimum version; log retention in days or months

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Must be secure" | 1 |
| Bad | "Data is encrypted" | 1 |
| Good | "Broken Access Control (OWASP Top 10:2025) is covered by authorization tests on every endpoint, with zero open high-severity findings" | 2 |
| Good | "TLS 1.2 or later for all external traffic; audit logs retained 12 months; verified by quarterly penetration test" | 3 |

### 3. Reliability

- **What to state**: availability, error rate, recovery time (RTO), recovery point (RPO), SLI/SLO definitions
- **Terms**: SLI is the measured indicator, SLO is the target for it (as defined in the Google SRE book)
- **Guidance range**: availability 99% to 99.99% by service criticality; RTO/RPO in minutes to hours

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Highly available" | 1 |
| Good | "Availability SLO 99.9% per month" | 2 |
| Good | "Availability SLO 99.9% per month, SLI = successful requests / total requests at the load balancer; RTO 1 hour, RPO 5 minutes; verified by a quarterly failover drill" | 3 |

### 4. Scalability

- **What to state**: supported users, data volume, growth rate, scale-out method
- **Guidance range**: current load and the multiple expected within the planning horizon (e.g., 10x in 2 years)

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Must be scalable" | 1 |
| Good | "Supports 10,000 concurrent users" | 2 |
| Good | "Supports 10,000 concurrent users and 1M records/day, scaling horizontally with p95 latency unchanged, verified by load test" | 3 |

### 5. Usability

- **What to state**: accessibility conformance, task completion time/rate, supported languages, learnability
- **Standards**: WCAG 2.2 (W3C Recommendation) with a conformance level (A, AA, AAA)
- **Guidance range**: Level AA is a common target for public-facing web UI

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Easy to use" | 1 |
| Good | "Conforms to WCAG 2.2 Level AA" | 2 |
| Good | "Conforms to WCAG 2.2 Level AA on the checkout flow, verified by automated scan plus manual screen-reader test; 90% of new users finish checkout without help" | 3 |

### 6. Maintainability

- **What to state**: test coverage, complexity limits, documentation, deploy frequency, time to fix
- **Guidance range**: coverage thresholds as a percentage of lines or branches; defect fix lead time in days

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Code should be maintainable" | 1 |
| Good | "Unit test line coverage of at least 80%" | 2 |
| Good | "Line coverage of at least 80% on core modules, verified by CI on every merge; critical defects fixed within 3 business days" | 3 |

### 7. Compatibility

- **What to state**: supported OS / browsers / runtimes (with versions), interoperability with external systems, data formats, API versioning
- **Guidance range**: a named list of supported versions or a support window (e.g., latest 2 major versions)

| Quality | Example | Level |
|:--------|:--------|:------|
| Bad | "Works on major browsers" | 1 |
| Good | "Latest 2 major versions of Chrome, Firefox, Safari, Edge" | 2 |
| Good | "Latest 2 major versions of Chrome, Firefox, Safari, Edge on desktop; verified by cross-browser E2E in CI; REST API backward compatible within a major version" | 3 |

## Notes

- Do not add maturity tiers (MVP / Production / Enterprise); ranges above are guidance only
- Cite standards by name and edition only; do not paraphrase their content
