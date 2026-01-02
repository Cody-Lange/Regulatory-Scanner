# SENTINEL SCAN - PROJECT BRIEF
**Last Updated:** January 2, 2026  
**Version:** 2.0 (Strategic Revision)  
**Status:** Pre-Launch / MVP Development

---

## REVISION NOTES (v2.0)

This document has been revised based on comprehensive strategic review. Key changes:
- **MVP scope expanded** to include VS Code extension (demo-critical)
- **Customer validation** added as prerequisite before full build
- **Pricing strategy** marked as hypothesis requiring validation
- **Go-to-market** includes concrete pipeline requirements
- **Healthcare** elevated as parallel vertical to test
- **Risk mitigation** enhanced with specific countermeasures
- **Timeline** adjusted to include validation week

---

## EXECUTIVE SUMMARY

**Company Name:** Sentinel Scan  
**Tagline:** Catch Data Privacy Violations Before They Cost Millions  
**Product:** Developer-native compliance scanning for LLM applications

**Core Problem:** Companies are rapidly adopting LLMs for analytics and automation, but accidentally exposing sensitive data (PII, VINs, PHI, financial records) to external APIs, risking fines up to €20M (GDPR) or $9.23M avg (HIPAA).

**Solution:** Static code analysis tool that scans developer code for compliance violations BEFORE deployment. Integrates into IDE (VS Code), Git, and CI/CD workflows. Blocks violations and generates audit trails.

**Target Market (Initial):** 
- **Primary:** Automotive manufacturers and dealers using LLMs for customer analytics
- **Parallel Test:** Healthcare organizations (higher urgency, stronger enforcement)

**Business Model:** SaaS subscriptions ($15K-$75K annually) + professional services for configuration and training.

**Traction Goal:** $100K ARR in Year 1 (4-5 customers), $500K in Year 2 (15 customers), $1.5M+ in Year 3 (35+ customers).

> ⚠️ **Revenue projections adjusted from v1.0** to reflect realistic first-year expectations and validated unit economics.

---

## CORE VALUE PROPOSITION

### The One-Liner
"Demonstrate compliance due diligence and create audit trails for your AI applications—catch data privacy violations in code before they reach production."

> 📝 **Change from v1.0:** Shifted from "prevent fines" (which ToS contradicts) to "demonstrate due diligence" (defensible, accurate).

### Why It Matters
- **Risk:** GDPR fines up to €20M or 4% global revenue; HIPAA breaches average $9.23M; Honda paid $632K for CCPA violations in 2024
- **Timing:** EU AI Act enforceable Feb 2025 (fines up to 7% revenue); California/Colorado laws active 2025-2026
- **Gap:** Current tools scan data at runtime (too late) or focus on general security (not compliance-specific)
- **Defensibility:** "We scanned every commit and blocked 47 violations before production" is a story compliance teams can tell regulators

### Key Differentiators
1. **Code-level scanning** (not just data-level) - catches violations where they're written
2. **LLM-workflow specific** - understands prompt construction, API calls, data serialization
3. **Developer-native** - integrates where developers work (IDE, Git hooks, CI/CD)
4. **Industry-specific templates** - pre-built rules for automotive, healthcare, finance
5. **Compliance expertise** - regulatory mapping, audit trails, not just pattern matching

### Positioning vs. "Just a Linter"

> ⚠️ **Critical Risk:** Sophisticated buyers may see regex pattern matching and question why they're paying $15K/year for something a senior engineer could build in a week.

**Our differentiation is NOT the technology—it's the compliance expertise baked in:**
- Pre-built detection rules maintained by compliance experts
- Regulatory mapping (violation → specific GDPR article, HIPAA rule)
- Audit-ready output for regulators and internal teams
- Continuous rule updates as regulations evolve
- Industry-specific patterns (VINs, PHI formats, financial data)
- Context-aware detection (distinguishing test data from production data)

---

## TARGET MARKET

### Primary Market (Year 1): Automotive + Healthcare (Parallel Testing)

**Automotive Segment:**
- **Size:** ~50 major manufacturers globally + top 100 dealer groups = ~150 enterprise targets
- **Use Cases:** Customer feedback analysis, sentiment tracking, campaign optimization, VIN-based analytics
- **Pain Point:** GDPR/CCPA compliance + automotive-specific data (VINs, service records, location data)
- **Strength:** Founder has domain expertise and existing network
- **Weakness:** Enforcement is sporadic; Honda fine ($632K) may not create sufficient urgency

**Healthcare Segment (Parallel Test):**
- **Size:** ~6,000 hospitals in US + health insurers + medical billing companies
- **Use Cases:** Patient communication automation, claims analysis, clinical decision support
- **Pain Point:** HIPAA compliance with $9.23M average breach cost; active enforcement
- **Strength:** Higher urgency, established compliance budgets, fear-driven purchasing
- **Weakness:** Longer sales cycles, more complex procurement

> 📝 **Strategy:** Run 5-10 discovery calls in EACH vertical during validation week. Let demand signals guide vertical prioritization, not assumptions.

### Buying Committee
- **Technical Buyer:** VP Data Science, Head of ML Engineering
- **Economic Buyer:** CTO, CDO, VP Engineering (controls budget)
- **Influencer:** General Counsel, Compliance Officer, Privacy Lead

> ⚠️ **Risk:** Champion (technical buyer) vs. budget holder (economic buyer) gap. Champion-led sales without direct path to economic buyer is how deals die in committee.

### Buyer Personas

**Persona 1: Technical Buyer (Data Science Lead)**
- Age: 32-45
- Role: Head of Data Science, ML Engineering Manager
- Pain: Team wants to use LLMs but compliance is blocking experiments
- Goal: Ship AI features faster without regulatory risk
- Objection: "We already have manual code review" / "This is just a linter"
- Win Condition: Show tool catches violations manual review misses; demonstrate context-aware detection

**Persona 2: Economic Buyer (VP Engineering / CDO)**
- Age: 40-55
- Role: VP Engineering, Chief Data Officer, CTO
- Pain: Board/Legal asking "Are we compliant?" - no good answer
- Goal: De-risk AI adoption, demonstrate due diligence
- Objection: "Is this really necessary?" / "Can't we build this ourselves?"
- Win Condition: ROI math + audit trail value + ongoing rule updates they can't replicate

**Persona 3: Influencer (Compliance/Legal)**
- Age: 35-50
- Role: General Counsel, Compliance Officer, Privacy Lead
- Pain: Can't keep up with engineering's AI experiments
- Goal: Audit trail, evidence of compliance for regulators
- Objection: "What about liability if your tool misses something?"
- Win Condition: Clear positioning as "decision support tool" with audit capabilities

---

## PRODUCT VISION

### MVP (Weeks 1-5) - REVISED

**Goal:** Prove the concept works, demonstrate value in demos, close first 2-3 design partners

> 📝 **Key Change:** VS Code extension added to MVP. CLI-only is insufficient for $15K enterprise sale. Developers need inline warnings as they type—pre-commit hooks catch violations too late in the workflow.

**Core Features:**

| Feature | Priority | Rationale |
|---------|----------|-----------|
| VS Code Extension | **P0** | Demo-critical; developers don't want CLI commands; inline warnings as they type |
| CLI tool scanning Python | **P0** | Required for CI/CD integration, pre-commit hooks |
| PII detection (emails, phones, SSNs, addresses) | **P0** | Core value proposition |
| VIN detection with checksum validation | **P0** | Automotive differentiator |
| YAML-based rule configuration | **P0** | Customization for enterprise |
| AST-based context analysis | **P0** | Distinguishes us from "just grep"; reduces false positives |
| False positive management (allowlists, inline ignores) | **P0** | Developers disable tools that cry wolf |
| Console + JSON output with violation details | **P1** | Audit trail capability |
| Pre-commit hook integration | **P1** | Developer workflow integration |
| Basic audit logging | **P1** | Compliance requirement |

**What We're NOT Building Yet:**
- ❌ Web dashboard/UI
- ❌ CI/CD platform integrations (GitHub Actions, GitLab CI)
- ❌ ML-based detection (Phase 2)
- ❌ Multi-language support (only Python)
- ❌ Real-time file watching
- ❌ Team collaboration features

### Detection Approach: Regex + AST (Not "Just Grep")

> ⚠️ **Critical:** The AST-based context analysis is what differentiates us from a simple linter. This MUST be in MVP.

**What AST analysis enables:**
- Detect if matched PII is in a string literal vs. variable name vs. comment
- Identify if data flows to LLM API calls (high priority) vs. just exists in code (medium priority)
- Distinguish test files/test data from production code
- Understand function context (is this in a `test_` function?)

**Priority tiers for violations:**
1. **CRITICAL:** Data sent directly to LLM API call (e.g., `openai.chat.completions.create()`)
2. **HIGH:** Data in variables that could be sent to LLM (requires data flow analysis)
3. **MEDIUM:** Hardcoded sensitive data in non-test files
4. **LOW/IGNORE:** Test data, comments, docstrings

### Phase 2 (Months 3-6)
- CI/CD integrations (GitHub Actions, GitLab CI, Jenkins)
- Web dashboard (violation trends, team analytics, compliance reports)
- JavaScript/TypeScript support
- Enhanced detection (ML-augmented for better context understanding)
- PyCharm plugin
- Healthcare compliance templates (HIPAA)

### Phase 3 (Months 6-12)
- Financial services templates (PCI-DSS, SOC2)
- Multi-language support (Java, Go, Ruby)
- Real-time scanning (file watchers)
- Team collaboration features (shared configs, exception approvals)
- Integration marketplace (Jira, Slack, ServiceNow)

### Long-term Vision (Year 2-3)
- Full compliance platform (not just LLM-focused)
- AI-powered rule generation from compliance documents
- Automated remediation suggestions
- Compliance certification workflows
- Partner ecosystem (consulting firms, analytics platforms)

---

## COMPETITIVE LANDSCAPE

### Direct Competitors
**None currently.** No one scans code specifically for LLM compliance violations.

### Adjacent Competitors & Our Response

| Category | Players | What They Do | What They Miss | Our Advantage |
|----------|---------|--------------|----------------|---------------|
| Data Privacy Platforms | OneTrust, BigID, Securiti | Data discovery, classification, inventory | Don't scan code; data-layer not dev-layer; expensive | Developer-native, code-level prevention |
| Code Security Scanners | Snyk, SonarQube, Checkmarx | Security vulns, code quality | Not compliance-focused; no LLM-specific; no industry templates | Compliance-first, LLM-aware, regulatory mapping |
| Data Anonymization | Gretel.ai, Private AI | Mask/synthesize sensitive data | Runtime solution (too late); doesn't prevent violations | Prevention at dev time, not remediation at runtime |
| API Monitors | Various gateways | Monitor API traffic | Only catch violations after deployment | Catch before production |

### Competitive Moat (What We're Building)

> ⚠️ **Reality Check:** Technology alone is NOT a moat. Snyk/SonarQube could add compliance rules in 6-12 months.

**Defensible advantages we must build:**
1. **Domain expertise:** Deep automotive/healthcare knowledge that takes years to develop
2. **Regulatory mapping database:** Pre-built connections between violations and specific regulations
3. **Customer relationships:** Early adopters become references, case studies, product advisors
4. **Rule library:** Continuously updated detection rules that customers can't replicate in-house
5. **Audit trail format:** Become the de facto standard for LLM compliance evidence

### Competitor Fast-Follow Response Plan

**If Snyk announces "Snyk Compliance for LLM Apps":**
- Accelerate healthcare/automotive specialization (generalists can't match domain depth)
- Lock in existing customers with annual contracts + deep integrations
- Emphasize regulatory mapping and audit trail features (not just detection)
- Position as "specialist vs. generalist" in messaging

---

## BUSINESS MODEL

### Revenue Streams

**Primary: SaaS Subscriptions (Target: 70% of revenue)**

| Tier | Price | Includes | Target Customer |
|------|-------|----------|-----------------|
| **Starter** | $15,000/year | Up to 5 developers, 1 project, pre-built templates, email support | Small teams, pilot phase |
| **Professional** | $35,000/year | Up to 20 developers, 5 projects, custom rules, priority support, quarterly reviews | Mid-market, multiple teams |
| **Enterprise** | $75,000+/year | Unlimited, dedicated CSM, SLA, custom integrations, on-prem option | Large orgs, complex needs |

> ⚠️ **PRICING IS HYPOTHESIS - NOT VALIDATED**
> 
> Before committing to development, we MUST validate willingness to pay through discovery calls. Current pricing is based on comparable security tools, not actual buyer conversations.
> 
> **Validation questions:**
> - "What would you expect to pay for this capability?"
> - "Does $15K/year cause sticker shock?"
> - "How does this compare to your security tool budget?"

**Secondary: Professional Services (Target: 30% of revenue in Year 1, declining to 10% by Year 3)**
- Implementation consulting: $150-250/hour
- Custom rule development: $10K-25K per engagement
- Compliance audit support: $25K-50K per engagement
- Training & enablement: $5K-15K per session

> 📝 **Warning:** If services becomes revenue driver, we're a consultancy with a tool, not a SaaS company. Monitor this ratio closely.

### Unit Economics (Target) - REVISED

| Metric | Year 1 Target | Notes |
|--------|---------------|-------|
| CAC | $8K-12K | Founder-led sales only |
| LTV | $50K-75K | Assumes 2-year retention (conservative) |
| LTV:CAC | 4:1 to 6:1 | Industry standard; 7:1+ is aspirational |
| Gross Margin | 85% blended | 90% software, 50% services |
| Payback Period | 6-9 months | On annual prepay deals |

> 📝 **Change from v1.0:** LTV reduced from $100-200K (which assumed 3-5 year retention) to $50-75K (assuming 2-year until we have data).

### Pricing Strategy
- **Land:** Start with Starter tier, minimize friction
- **Expand:** Grow to Pro as teams adopt, then Enterprise as org standardizes
- **Services:** Upsell consulting after initial success, not during sales
- **Discounts:** 20-30% off for annual prepay, design partners, multi-year commitments

---

## GO-TO-MARKET STRATEGY

### Pre-Phase: Customer Validation (Week 1) - NEW

> 🚨 **CRITICAL:** This phase is MANDATORY before committing to full MVP development.

**Goal:** Validate demand, pricing, and feature priorities through direct buyer conversations

**Activities:**
- Schedule 10 discovery calls (5 automotive, 5 healthcare)
- Show wireframes/mockups of VS Code extension and CLI output
- Validate pain points and willingness to pay
- Identify 1-2 design partners willing to beta test

**Validation Criteria (must achieve to proceed):**
- [ ] 10 completed discovery calls
- [ ] At least 6/10 express strong interest ("I would use this")
- [ ] No sticker shock at $15K price point (or clear signal on acceptable price)
- [ ] At least 1 design partner committed (free usage for 6 months in exchange for feedback)

**If validation fails:**
- Revisit pricing (maybe $5K-$10K tier needed)
- Revisit vertical (maybe neither automotive nor healthcare is right)
- Revisit product (maybe different feature set needed)

### Phase 1: Automotive + Healthcare Beachhead (Months 1-4)

**Goal:** 3-4 paying customers, $60K-80K ARR, proven playbook

> 📝 **Change from v1.0:** Revenue target reduced from $125K to $80K based on realistic conversion rates.

**Pipeline Requirements:**
| Metric | Target | Math |
|--------|--------|------|
| Target accounts (named) | 30 | 15 automotive + 15 healthcare |
| Discovery calls | 20 | 66% of targets agree to call |
| Qualified opportunities | 10 | 50% qualify as real opportunity |
| Pilots initiated | 6 | 60% agree to pilot |
| Closed deals | 3-4 | 50-66% pilot-to-close |

> ⚠️ **Requirement:** Before starting Phase 1, we must have a LIST OF 30 NAMED ACCOUNTS with specific contacts identified. "Warm network" is not a pipeline.

**Tactics:**
- Direct outreach to named accounts from validation phase
- Design partner case study (anonymized initially, named if permitted)
- Conference presence: Automotive AI Summit, HIMSS (healthcare IT)
- Content: "The Hidden Compliance Risks in AI Applications" whitepaper
- Referral asks from every customer conversation

**Metrics to Track:**
- Demo-to-pilot conversion rate (target: 50%+)
- Pilot-to-close conversion rate (target: 50%+)
- Average sales cycle length (target: 60-90 days)
- Win/loss reasons for every deal

### Phase 2: Scale Within Verticals (Months 4-12)

**Goal:** 12-15 customers, $350K-500K ARR

**Tactics:**
- Hire Sales Rep #1 (only after proving repeatable playbook)
- Expand content marketing (SEO, thought leadership)
- Build referral program (10% commission for customer referrals)
- Partner exploratory talks with consulting firms
- Launch customer advisory board

### Phase 3: Multi-Vertical Expansion (Months 12-24)

**Goal:** 30-40 customers, $1M-1.5M ARR

**Tactics:**
- Launch finance templates, test financial services vertical
- Hire vertical-specific sales reps
- Series A consideration ($3M-5M) OR continue bootstrapping if profitable
- Build partner ecosystem (5-10 consulting/implementation partners)

---

## TECHNICAL ARCHITECTURE

*See TECHNICAL_SPEC.md for full details*

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENTINEL SCAN SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                    ┌──────────────────┐  │
│  │  VS Code Plugin  │◄──── shared ──────►│    CLI Tool      │  │
│  │  (P0 for MVP)    │      engine        │  (P0 for MVP)    │  │
│  └────────┬─────────┘                    └────────┬─────────┘  │
│           │                                       │             │
│           ▼                                       ▼             │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                    DETECTION ENGINE                        ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐││
│  │  │   Regex     │  │     AST     │  │   Context           │││
│  │  │  Detectors  │  │   Parser    │  │   Analyzer          │││
│  │  │  (PII, VIN) │  │  (Python)   │  │  (LLM API flows)    │││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘││
│  └────────────────────────────────────────────────────────────┘│
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                      RULE ENGINE                           ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐││
│  │  │   YAML      │  │  Industry   │  │   Allowlists &      │││
│  │  │   Config    │  │  Templates  │  │   FP Management     │││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘││
│  └────────────────────────────────────────────────────────────┘│
│           │                                                     │
│           ▼                                                     │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                    OUTPUT LAYER                            ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐││
│  │  │   VS Code   │  │   Console   │  │      JSON           │││
│  │  │  Diagnostics│  │   Output    │  │   Audit Logs        │││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Target language, rich AST support |
| CLI Framework | Typer | Modern Click alternative, better type hints |
| VS Code Extension | TypeScript | Required for VS Code extensions |
| Config Format | YAML (PyYAML) | Human-readable, supports comments |
| AST Parsing | Python `ast` module | Built-in, no dependencies |
| Testing | pytest | Industry standard |
| Distribution | PyPI + VS Code Marketplace | Standard distribution channels |

### Performance Targets

| Metric | Target | Stretch |
|--------|--------|---------|
| Scan Speed | <5s for 10K lines | <2s for 10K lines |
| VS Code Diagnostics | <500ms per file | <200ms per file |
| False Positive Rate | <5% | <2% |
| False Negative Rate (Critical) | <1% | <0.1% |

---

## KEY METRICS & GOALS

### Product Metrics
- **Detection Accuracy:** 95%+ true positive rate, <5% false positive rate
- **Performance:** VS Code diagnostics <500ms per file; CLI scan <1s per 1000 lines
- **Coverage:** Support 90%+ of common PII patterns + VIN validation

### Business Metrics (Year 1) - REVISED

| Metric | Target | Stretch |
|--------|--------|---------|
| Revenue | $100K ARR | $150K ARR |
| Customers | 4-5 paying | 8 paying |
| ACV | $22K | $25K |
| Pipeline | $300K qualified by Q2 | $500K |
| Win Rate | 30%+ | 40%+ |
| Retention | 90%+ | 95%+ |

> 📝 **Change from v1.0:** Year 1 targets reduced from $150K/6 customers to $100K/4-5 customers based on realistic first-year expectations.

### Business Metrics (Year 2)
- Revenue: $500K ARR
- Customers: 15 paying
- ACV: $33K
- New Hires: 1 sales rep, 1 engineer

### Business Metrics (Year 3)
- Revenue: $1.5M ARR
- Customers: 35+ paying
- Multiple verticals active
- Team Size: 6-8 people

---

## MILESTONES & TIMELINE - REVISED

### Week 0: Customer Validation (MANDATORY)
- [ ] Schedule 10 discovery calls (5 automotive, 5 healthcare)
- [ ] Create wireframes/mockups for demos
- [ ] Conduct calls, document feedback
- [ ] Identify at least 1 design partner
- [ ] Go/no-go decision on MVP development

### Weeks 1-2: Core Engine
- [ ] Detection engine with regex + AST analysis
- [ ] PII detectors (email, phone, SSN, address)
- [ ] VIN detector with checksum validation
- [ ] YAML config loading
- [ ] Context analyzer (test vs. production, LLM API flows)

### Weeks 3-4: VS Code Extension + CLI
- [ ] VS Code extension with inline diagnostics
- [ ] CLI tool with scan command
- [ ] Console output formatting
- [ ] JSON export for audit logs
- [ ] Pre-commit hook generation

### Week 5: Polish + Design Partner Deploy
- [ ] False positive management (allowlists, inline ignores)
- [ ] Documentation
- [ ] Deploy to design partner
- [ ] Gather feedback, iterate

### Weeks 6-8: First Customers
- [ ] First paid customer closed
- [ ] Case study development (with design partner)
- [ ] Landing page live
- [ ] Begin Phase 1 GTM execution

### Q2 2025 (Months 3-5)
- [ ] 3-4 total customers
- [ ] CI/CD integrations development started
- [ ] Healthcare templates if healthcare shows demand

### Q3-Q4 2025 (Months 6-12)
- [ ] 12-15 customers
- [ ] First sales hire
- [ ] Web dashboard beta
- [ ] Multi-language support planning

---

## RISKS & MITIGATION - ENHANCED

### Risk Matrix

| Rank | Risk | Likelihood | Impact | Mitigation |
|------|------|------------|--------|------------|
| 1 | **Unvalidated pricing/demand** | High | Critical | Validation week BEFORE coding; 10 discovery calls |
| 2 | **"Just a linter" perception** | High | High | AST analysis in MVP; lead with compliance expertise |
| 3 | **Developer adoption failure (FP rate)** | Medium | Critical | FP management in MVP; obsess over accuracy |
| 4 | **Champion vs. budget holder gap** | High | High | Map buying committee early; get economic buyer intro |
| 5 | **"Build vs. buy" objection** | Medium | High | Emphasize ongoing rule updates, regulatory mapping |
| 6 | **Competitor fast-follow** | Medium | Medium | Build domain expertise moat; lock in early customers |
| 7 | **Liability concerns** | Low-Medium | Medium | Clear ToS; E&O insurance; "decision support" positioning |
| 8 | **Long sales cycles** | High | Medium | Target mid-market first; offer monthly pilots |

### Detailed Risk Analysis

**Risk 1: Unvalidated Pricing/Demand**
- **What could go wrong:** We build a product nobody wants at a price nobody will pay
- **Early warning signs:** Can't get discovery calls; sticker shock in conversations; "interesting but not urgent"
- **Mitigation:** Mandatory validation week; 10 conversations before coding; design partner commitment required

**Risk 2: "Just a Linter" Perception**
- **What could go wrong:** Sophisticated buyers see regex matching and dismiss us
- **Early warning signs:** "We could build this ourselves" objection; low perceived value
- **Mitigation:** AST analysis in MVP; lead with compliance expertise not technology; show regulatory mapping

**Risk 3: Developer Adoption Failure**
- **What could go wrong:** High false positive rate causes developers to disable the tool
- **Early warning signs:** Tool disabled in first week; complaints about noise; workarounds emerging
- **Mitigation:** FP management in MVP; configurable strictness; fast iteration on feedback

**Risk 4: Champion vs. Budget Holder Gap**
- **What could go wrong:** Technical champion loves it but can't get budget approval
- **Early warning signs:** Long deal cycles; "I need to check with..." repeatedly; stuck in pilot
- **Mitigation:** Map buying committee early; get economic buyer intro in first meeting; ROI calculator

**Risk 5: "Build vs. Buy" Objection**
- **What could go wrong:** At $15K+, companies evaluate building internally
- **Early warning signs:** "Let me check with engineering" followed by silence; RFP process
- **Mitigation:** Emphasize ongoing rule updates; regulatory expertise; audit trail format; "total cost of ownership" comparison

---

## OPEN QUESTIONS - PRIORITIZED

### Must Answer Before Building (Validation Week)
- [ ] Is automotive or healthcare the better starting vertical?
- [ ] Does $15K pricing cause sticker shock?
- [ ] Is VS Code extension truly critical or nice-to-have?
- [ ] What features would make this a "must have" vs. "nice to have"?

### Must Answer Before First Customer
- [ ] What's our response when a customer using Sentinel Scan gets fined anyway?
- [ ] Do we need E&O insurance from Day 1?
- [ ] What's the minimum viable audit trail format?

### Can Answer With Customer Data
- [ ] Annual contracts only, or offer monthly for SMBs?
- [ ] Should we take investment in Year 1?
- [ ] What's the right team size for $500K ARR?
- [ ] Do we need SOC2 compliance? When?

---

## KEY DECISIONS LOG

| Date | Decision | Rationale | Owner |
|------|----------|-----------|-------|
| Jan 2, 2026 | Add VS Code extension to MVP | Demo-critical; CLI-only insufficient for enterprise sale | Cody |
| Jan 2, 2026 | Add mandatory validation week | De-risk development; validate demand and pricing | Cody |
| Jan 2, 2026 | Test healthcare in parallel | Higher urgency than automotive; stronger enforcement | Cody |
| Jan 2, 2026 | Reduce Year 1 targets | Original projections optimistic; set realistic bar | Cody |
| Jan 2, 2026 | AST analysis required in MVP | Differentiates from "just grep"; reduces FP rate | Cody |
| Jan 2, 2026 | FP management in MVP | Developers disable noisy tools; table stakes | Cody |

---

## IMMEDIATE NEXT STEPS (Prioritized)

1. **This Week: Schedule Validation Calls**
   - Create list of 30 target accounts (15 automotive, 15 healthcare)
   - Identify specific contacts at each
   - Send outreach; book 10 discovery calls

2. **This Week: Create Demo Materials**
   - Wireframes of VS Code extension showing inline warnings
   - Mockup of CLI output with violation details
   - One-pager explaining value proposition

3. **This Week: Competitive Intel**
   - Sign up for Snyk free tier; understand their UX
   - Request OneTrust/BigID demos
   - Document exactly what they do and don't do

4. **Week 1: Conduct Validation Calls**
   - Run all 10 discovery calls
   - Document pain points, feature priorities, pricing feedback
   - Identify design partner

5. **Week 1: Go/No-Go Decision**
   - Review validation results
   - Commit to MVP scope or pivot
   - Begin development if validation passes

---

## RESOURCES & LINKS

### Internal Documents
- Technical Specification: `TECHNICAL_SPEC_v2.md`
- Market Research: `MARKET_RESEARCH.md` (to be created)
- Validation Call Script: `VALIDATION_SCRIPT.md` (to be created)
- Competitive Analysis: `COMPETITIVE_ANALYSIS.md` (to be created)

### Design Reference
- Landing Page Inspiration: snyk.io, linear.app, vercel.com
- VS Code Extension Examples: ESLint, Prettier, SonarLint

---

## FOUNDER BIO

**Cody Lange**
- Background: Data scientist with automotive industry experience
- Current: Consulting for major automotive OEM (Ford/OneMagnify network)
- Expertise: LLMs, data privacy regulations, automotive analytics
- Origin Story: Caught major compliance violation days before production, realized this happens everywhere
- Why Now: Living the problem daily, perfect timing with new regulations

---

## CONTACT & STATUS

**Founder:** Cody Lange  
**Email:** cody@sentinelscan.io  
**Status:** Pre-validation, preparing for discovery calls

---

*Last updated: January 2, 2026*  
*Next review: After validation week completion*
