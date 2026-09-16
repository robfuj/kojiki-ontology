---
name: agency-agents
description: "Skill registry mapping available skills to department agents in the decision system."
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [skill-registry, department-agents, skill-mapping, decision-systems]
  homepage: https://github.com/decision-systems/skills/agency-agents
  related_skills: [deck-builder, github-autodiscovery, multi-agent-orchestration, specialist-builder]
---

# Agency Agents — Department Skill Registry

This skill defines which skills are available to each department agent. Agents in each department load their assigned skills at runtime to extend their capabilities.

## Available Skills in This Repo

| Skill | Path | Description |
|-------|------|-------------|
| **deck-builder** | `skills/deck-builder/` | Generate presentation decks in 7 modes with embedded charts, templates, and consulting frameworks |
| **github-autodiscovery** | `skills/github-autodiscovery/` | Auto-discover and secure GitHub repositories for specialists; includes PR workflow, issues, code review |
| **multi-agent-orchestration** | `skills/multi-agent-orchestration/` | Coordinate multiple agents in parallel with dependency management and conflict resolution |
| **specialist-builder** | `skills/specialist-builder/` | Build Kojiki department specialists with shared core runner, scaffolding, and validation |

---

## Agency-Agents Skills Mapping (from msitarzewski/agency-agents)

The following individual agent skills from the agency-agents repository are mapped to our departments. Each agent file contains identity, workflows, deliverables, and success metrics.

### Engineering Division (70+ agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Frontend Developer | `engineering/engineering-frontend-developer.md` | React/Vue/Angular, UI implementation, performance |
| Backend Architect | `engineering/engineering-backend-architect.md` | API design, database architecture, scalability |
| Mobile App Builder | `engineering/engineering-mobile-app-builder.md` | iOS/Android, React Native, Flutter |
| AI Engineer | `engineering/engineering-ai-engineer.md` | ML models, deployment, AI integration |
| DevOps Automator | `engineering/engineering-devops-automator.md` | CI/CD, infrastructure automation, cloud ops |
| SRE | `engineering/engineering-sre.md` | SLOs, error budgets, observability, chaos engineering |
| Software Architect | `engineering/engineering-software-architect.md` | System design, DDD, architectural patterns |
| Security Architect | `security/security-architect.md` | Threat modeling, secure-by-design |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | Constructive code review, security, maintainability |
| Database Optimizer | `engineering/engineering-database-optimizer.md` | Schema design, query optimization, indexing |
| Multi-Agent Systems Architect | `engineering/engineering-multi-agent-systems-architect.md` | Multi-agent pipeline design & governance |
| Platform Engineer | `engineering/engineering-platform-engineer.md` | Internal developer platforms, golden paths, IDPs |
| API Platform Engineer | `engineering/engineering-api-platform-engineer.md` | API gateways & platforms |
| RAG Pipeline Engineer | `engineering/engineering-rag-pipeline-engineer.md` | Production RAG pipelines |
| LLM Post-Training Engineer | `engineering/engineering-llm-post-training-engineer.md` | Post-training stack (SFT/DPO/GRPO/RLVR) |
| Data Visualization Engineer | `engineering/engineering-data-visualization-engineer.md` | Perceptually honest data viz |

### Design Division (10+ agents)
| Agent | File | Specialty |
|-------|------|-----------|
| UI Designer | `design/design-ui-designer.md` | Visual design, component libraries, design systems |
| UX Researcher | `design/design-ux-researcher.md` | User testing, behavior analysis, research |
| UX Architect | `design/design-ux-architect.md` | Technical architecture, CSS systems, implementation |
| Brand Guardian | `design/design-brand-guardian.md` | Brand identity, consistency, positioning |
| Visual Storyteller | `design/design-visual-storyteller.md` | Visual narratives, multimedia content |
| Whimsy Injector | `design/design-whimsy-injector.md` | Personality, delight, playful interactions |
| Image Prompt Engineer | `design/design-image-prompt-engineer.md` | AI image generation prompts |
| Inclusive Visuals Specialist | `design/design-inclusive-visuals-specialist.md` | Representation, bias mitigation, authentic imagery |
| UI Finish-Gate Reviewer | `design/design-ui-finish-gate-reviewer.md` | Anti-generic UI finish gate |

### Paid Media Division (8 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| PPC Campaign Strategist | `paid-media/paid-media-ppc-strategist.md` | Google/Microsoft/Amazon Ads, account architecture |
| Search Query Analyst | `paid-media/paid-media-search-query-analyst.md` | Search term analysis, negative keywords |
| Paid Media Auditor | `paid-media/paid-media-auditor.md` | 200+ point account audits, competitive analysis |
| Tracking & Measurement Specialist | `paid-media/paid-media-tracking-specialist.md` | GTM, GA4, conversion tracking, CAPI |
| Ad Creative Strategist | `paid-media/paid-media-creative-strategist.md` | RSA copy, Meta creative, Performance Max assets |
| Programmatic & Display Buyer | `paid-media/paid-media-programmatic-buyer.md` | GDN, DSPs, partner media, ABM display |
| Paid Social Strategist | `paid-media/paid-media-paid-social-strategist.md` | Meta, LinkedIn, TikTok, cross-platform social |

### Sales Division (9 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Outbound Strategist | `sales/sales-outbound-strategist.md` | Signal-based prospecting, multi-channel sequences |
| Discovery Coach | `sales/sales-discovery-coach.md` | SPIN, Gap Selling, Sandler — question design |
| Deal Strategist | `sales/sales-deal-strategist.md` | MEDDPICC qualification, competitive positioning |
| Sales Engineer | `sales/sales-engineer.md` | Technical demos, POC scoping, battlecards |
| Proposal Strategist | `sales/sales-proposal-strategist.md` | RFP response, win themes, narrative structure |
| Pipeline Analyst | `sales/sales-pipeline-analyst.md` | Forecasting, pipeline health, deal velocity, RevOps |
| Account Strategist | `sales/sales-account-strategist.md` | Land-and-expand, QBRs, stakeholder mapping |
| Sales Coach | `sales/sales-coach.md` | Rep development, call coaching, pipeline review |

### Marketing Division (40+ agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Growth Hacker | `marketing/marketing-growth-hacker.md` | Rapid user acquisition, viral loops, experiments |
| Content Creator | `marketing/marketing-content-creator.md` | Multi-platform content, editorial calendars |
| Twitter Engager | `marketing/marketing-twitter-engager.md` | Real-time engagement, thought leadership |
| X/Twitter Intelligence Analyst | `marketing/marketing-x-twitter-intelligence-analyst.md` | Social listening, trend detection, account monitoring |
| SEO Specialist | `marketing/marketing-seo-specialist.md` | Technical SEO, content strategy, link building |
| App Store Optimizer | `marketing/marketing-app-store-optimizer.md` | ASO, conversion optimization, discoverability |
| Social Media Strategist | `marketing/marketing-social-media-strategist.md` | Cross-platform strategy, campaigns |
| Carousel Growth Engine | `marketing/marketing-carousel-growth-engine.md` | TikTok/Instagram carousels, autonomous publishing |
| LinkedIn Content Creator | `marketing/marketing-linkedin-content-creator.md` | Personal branding, thought leadership, B2B content |
| Email Marketing Strategist | `marketing/marketing-email-strategist.md` | Lifecycle email & deliverability |
| PR & Communications Manager | `marketing/marketing-pr-communications-manager.md` | PR, media relations & crisis comms |
| AI Citation Strategist | `marketing/marketing-ai-citation-strategist.md` | AEO/GEO, AI recommendation visibility |
| AEO Foundations Architect | `marketing/marketing-aeo-foundations.md` | AI Engine Optimization infrastructure |
| Agentic Search Optimizer | `marketing/marketing-agentic-search-optimizer.md` | WebMCP & agentic task completion |
| Video Optimization Specialist | `marketing/marketing-video-optimization-specialist.md` | YouTube algorithm strategy, chaptering |

### Product Division (5 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Sprint Prioritizer | `product/product-sprint-prioritizer.md` | Agile planning, feature prioritization |
| Trend Researcher | `product/product-trend-researcher.md` | Market intelligence, competitive analysis |
| Feedback Synthesizer | `product/product-feedback-synthesizer.md` | User feedback analysis, insights extraction |
| Behavioral Nudge Engine | `product/product-behavioral-nudge-engine.md` | Behavioral psychology, nudge design |
| Product Manager | `product/product-manager.md` | Full lifecycle product ownership |

### Project Management Division (7 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Studio Producer | `project-management/project-management-studio-producer.md` | High-level orchestration, portfolio management |
| Project Shepherd | `project-management/project-management-project-shepherd.md` | Cross-functional coordination, timeline management |
| Studio Operations | `project-management/project-management-studio-operations.md` | Day-to-day efficiency, process optimization |
| Experiment Tracker | `project-management/project-management-experiment-tracker.md` | A/B tests, hypothesis validation |
| Senior Project Manager | `project-management/project-manager-senior.md` | Realistic scoping, task conversion |
| Jira Workflow Steward | `project-management/project-management-jira-workflow-steward.md` | Git workflow, branch strategy, traceability |
| Meeting Notes Specialist | `project-management/project-management-meeting-notes-specialist.md` | Structured meeting summaries |

### Testing Division (9 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Evidence Collector | `testing/testing-evidence-collector.md` | Screenshot-based QA, visual proof |
| Reality Checker | `testing/testing-reality-checker.md` | Evidence-based certification, quality gates |
| Test Results Analyzer | `testing/testing-test-results-analyzer.md` | Test evaluation, metrics analysis |
| Performance Benchmarker | `testing/testing-performance-benchmarker.md` | Performance testing, optimization |
| API Tester | `testing/testing-api-tester.md` | API validation, integration testing |
| Tool Evaluator | `testing/testing-tool-evaluator.md` | Technology assessment, tool selection |
| Workflow Optimizer | `testing/testing-workflow-optimizer.md` | Process analysis, workflow improvement |
| Accessibility Auditor | `testing/testing-accessibility-auditor.md` | WCAG auditing, assistive technology testing |
| Test Automation Engineer | `testing/testing-test-automation-engineer.md` | Playwright/Cypress E2E, flake elimination |

### Security Division (12 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Security Architect | `security/security-architect.md` | Threat modeling, secure-by-design, trust boundaries |
| Application Security Engineer | `security/security-appsec-engineer.md` | SDLC security, SAST/DAST, secure code review |
| Penetration Tester | `security/security-penetration-tester.md` | Authorized pentests, red team ops |
| Cloud Security Architect | `security/security-cloud-security-architect.md` | Zero trust, cloud-native defense-in-depth |
| Incident Responder | `security/security-incident-responder.md` | DFIR, breach investigation, threat containment |
| Threat Intelligence Analyst | `security/security-threat-intelligence-analyst.md` | Adversary tracking, campaign mapping, ATT&CK |
| Threat Detection Engineer | `security/security-threat-detection-engineer.md` | SIEM rules, threat hunting, ATT&CK mapping |
| Compliance Auditor | `security/security-compliance-auditor.md` | SOC 2, ISO 27001, HIPAA, PCI-DSS |
| AI-Generated Code Security Auditor | `security/security-ai-generated-code-auditor.md` | Security review of AI/vibe-coded apps |
| Secrets & Credential Hygiene Engineer | `security/security-secrets-credential-engineer.md` | Secrets & credential lifecycle |

### Support Division (7 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Support Responder | `support/support-support-responder.md` | Customer service, issue resolution |
| Analytics Reporter | `support/support-analytics-reporter.md` | Data analysis, dashboards, insights |
| Finance Tracker | `support/support-finance-tracker.md` | Financial planning, budget management |
| Infrastructure Maintainer | `support/support-infrastructure-maintainer.md` | System reliability, performance optimization |
| Legal Compliance Checker | `support/support-legal-compliance-checker.md` | Compliance, regulations, legal review |
| Executive Summary Generator | `support/support-executive-summary-generator.md` | C-suite communication, strategic summaries |

### Finance Division (6 agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Bookkeeper & Controller | `finance/finance-bookkeeper-controller.md` | Month-end close, reconciliation, GAAP compliance |
| Financial Analyst | `finance/finance-financial-analyst.md` | Financial modeling, forecasting, scenario analysis |
| FP&A Analyst | `finance/finance-fpa-analyst.md` | Budgeting, rolling forecasts, variance analysis |
| Investment Researcher | `finance/finance-investment-researcher.md` | Due diligence, portfolio analysis, asset valuation |
| Tax Strategist | `finance/finance-tax-strategist.md` | Tax optimization, multi-jurisdictional compliance |

### Specialized Division (50+ agents)
| Agent | File | Specialty |
|-------|------|-----------|
| Agents Orchestrator | `specialized/agents-orchestrator.md` | Multi-agent coordination, workflow management |
| Chief of Staff | `specialized/specialized-chief-of-staff.md` | Executive coordination |
| Business Strategist | `specialized/business-strategist.md` | Management-consulting strategy |
| Change Management Consultant | `specialized/change-management-consultant.md` | ADKAR/Kotter/Prosci change |
| Customer Success Manager | `specialized/customer-success-manager.md` | Onboarding, health & retention |
| Operations Manager | `specialized/operations-manager.md` | Lean/Six Sigma operations |
| Organizational Psychologist | `specialized/organizational-psychologist.md` | Team dynamics & culture health |
| Recruitment Specialist | `specialized/recruitment-specialist.md` | Talent acquisition, recruiting operations |
| HR Onboarding | `specialized/hr-onboarding.md` | Pre-boarding, compliance, benefits enrollment |
| Data Privacy Officer | `specialized/data-privacy-officer.md` | GDPR/CCPA privacy compliance |
| Chief Financial Officer | `specialized/chief-financial-officer.md` | Capital allocation & financial strategy |
| Legal Document Review | `specialized/legal-document-review.md` | Contract review, risk flagging, version comparison |
| Compliance Auditor | `security/security-compliance-auditor.md` | SOC 2, ISO 27001, HIPAA, PCI-DSS |
| MCP Builder | `specialized/specialized-mcp-builder.md` | Model Context Protocol servers |
| Document Generator | `specialized/specialized-document-generator.md` | PDF, PPTX, DOCX, XLSX generation from code |
| Automation Governance Architect | `specialized/automation-governance-architect.md` | Automation governance, n8n, workflow auditing |
| Codebase Archaeologist | `specialized/specialized-codebase-archaeologist.md` | Multi-tool codebase drift audits |
| Agentic Identity & Trust Architect | `specialized/agentic-identity-trust.md` | Agent identity, authentication, trust verification |
| Identity Graph Operator | `specialized/identity-graph-operator.md` | Shared identity resolution for multi-agent systems |

---

## Skill Assignments by Department

### Finance
**Core Skills:** `deck-builder`, `github-autodiscovery`
**Agency-Agents Skills:**
- `finance/finance-bookkeeper-controller.md` — Month-end close, reconciliation, GAAP compliance
- `finance/finance-financial-analyst.md` — Financial modeling, forecasting, scenario analysis
- `finance/finance-fpa-analyst.md` — Budgeting, rolling forecasts, variance analysis
- `finance/finance-investment-researcher.md` — Due diligence, portfolio analysis, asset valuation
- `finance/finance-tax-strategist.md` — Tax optimization, multi-jurisdictional compliance
- `specialized/chief-financial-officer.md` — Capital allocation & financial strategy
- `specialized/pricing-analyst.md` — Pricing models & margin optimization
- `specialized/accounts-payable-agent.md` — Payment processing, vendor management, audit
- `specialized/loan-officer-assistant.md` — Borrower intake, TRID compliance, pipeline tracking
- `specialized/medical-billing-coding-specialist.md` — ICD-10/CPT/HCPCS & revenue cycle
- `specialized/grant-writer.md` — Grant proposals & funding
- `specialized/esg-sustainability-officer.md` — ESG programs & disclosure
- `support/support-finance-tracker.md` — Financial planning, budget management
**Use Cases:**
- `deck-builder`: Board decks, investor updates, budget presentations, FP&A reviews
- `github-autodiscovery`: Find financial modeling repos, accounting automation tools, treasury management repos

### Marketing
**Core Skills:** `deck-builder`, `github-autodiscovery`, `multi-agent-orchestration`
**Agency-Agents Skills:**
- `marketing/marketing-growth-hacker.md` — Rapid user acquisition, viral loops, experiments
- `marketing/marketing-content-creator.md` — Multi-platform content, editorial calendars
- `marketing/marketing-seo-specialist.md` — Technical SEO, content strategy, link building
- `marketing/marketing-social-media-strategist.md` — Cross-platform strategy, campaigns
- `marketing/marketing-carousel-growth-engine.md` — TikTok/Instagram carousels, autonomous publishing
- `marketing/marketing-linkedin-content-creator.md` — Personal branding, thought leadership, B2B content
- `marketing/marketing-email-strategist.md` — Lifecycle email & deliverability
- `marketing/marketing-pr-communications-manager.md` — PR, media relations & crisis comms
- `marketing/marketing-ai-citation-strategist.md` — AEO/GEO, AI recommendation visibility
- `marketing/marketing-aeo-foundations.md` — AI Engine Optimization infrastructure
- `marketing/marketing-agentic-search-optimizer.md` — WebMCP & agentic task completion
- `marketing/marketing-video-optimization-specialist.md` — YouTube algorithm strategy, chaptering
- `design/design-ui-designer.md` — Visual design, component libraries, design systems
- `design/design-ux-researcher.md` — User testing, behavior analysis, research
- `design/design-ux-architect.md` — Technical architecture, CSS systems, implementation
- `design/design-brand-guardian.md` — Brand identity, consistency, positioning
- `design/design-visual-storyteller.md` — Visual narratives, multimedia content
- `design/design-whimsy-injector.md` — Personality, delight, playful interactions
- `design/design-image-prompt-engineer.md` — AI image generation prompts
- `design/design-inclusive-visuals-specialist.md` — Representation, bias mitigation, authentic imagery
- `design/design-ui-finish-gate-reviewer.md` — Anti-generic UI finish gate
- `paid-media/paid-media-ppc-strategist.md` — Google/Microsoft/Amazon Ads, account architecture
- `paid-media/paid-media-creative-strategist.md` — RSA copy, Meta creative, Performance Max assets
- `paid-media/paid-media-paid-social-strategist.md` — Meta, LinkedIn, TikTok, cross-platform social
- `specialized/cultural-intelligence-strategist.md` — Global UX, representation, cultural exclusion
- `specialized/healthcare-marketing-compliance.md` — China healthcare advertising compliance
**Use Cases:**
- `deck-builder`: Campaign decks, brand guidelines, pitch decks, carousel slides, reel analysis
- `github-autodiscovery`: Marketing automation repos, analytics dashboards, SEO tooling
- `multi-agent-orchestration`: Coordinate campaign agents (content, paid, SEO, social) in parallel

### Sales
**Core Skills:** `deck-builder`, `github-autodiscovery`, `multi-agent-orchestration`
**Agency-Agents Skills:**
- `sales/sales-outbound-strategist.md` — Signal-based prospecting, multi-channel sequences
- `sales/sales-discovery-coach.md` — SPIN, Gap Selling, Sandler — question design
- `sales/sales-deal-strategist.md` — MEDDPICC qualification, competitive positioning
- `sales/sales-engineer.md` — Technical demos, POC scoping, battlecards
- `sales/sales-proposal-strategist.md` — RFP response, win themes, narrative structure
- `sales/sales-pipeline-analyst.md` — Forecasting, pipeline health, deal velocity, RevOps
- `sales/sales-account-strategist.md` — Land-and-expand, QBRs, stakeholder mapping
- `sales/sales-coach.md` — Rep development, call coaching, pipeline review
- `specialized/sales-outreach.md` — Cold prospecting, multi-touch cadences, objection handling
- `specialized/sales-offer-lead-gen-strategist.md` — Offers & lead magnets
- `specialized/sales-data-extraction-agent.md` — Excel monitoring, sales metric extraction
- `specialized/data-consolidation-agent.md` — Sales data aggregation, dashboard reports
- `specialized/report-distribution-agent.md` — Automated report delivery
- `specialized/salesforce-architect.md` — Multi-cloud Salesforce design, governor limits, integrations
**Use Cases:**
- `deck-builder`: Proposal decks, pitch decks, client presentations, follow-up materials
- `github-autodiscovery`: CRM integrations, outreach automation, lead enrichment tools
- `multi-agent-orchestration`: Coordinate outbound, growth, biz dev, corp dev agents

### Engineering
**Core Skills:** `github-autodiscovery`, `specialist-builder`, `multi-agent-orchestration`
**Agency-Agents Skills:**
- `engineering/engineering-frontend-developer.md` — React/Vue/Angular, UI implementation, performance
- `engineering/engineering-backend-architect.md` — API design, database architecture, scalability
- `engineering/engineering-ai-engineer.md` — ML models, deployment, AI integration
- `engineering/engineering-devops-automator.md` — CI/CD, infrastructure automation, cloud ops
- `engineering/engineering-sre.md` — SLOs, error budgets, observability, chaos engineering
- `engineering/engineering-software-architect.md` — System design, DDD, architectural patterns
- `engineering/engineering-code-reviewer.md` — Constructive code review, security, maintainability
- `engineering/engineering-database-optimizer.md` — Schema design, query optimization, indexing
- `engineering/engineering-multi-agent-systems-architect.md` — Multi-agent pipeline design & governance
- `engineering/engineering-platform-engineer.md` — Internal developer platforms, golden paths, IDPs
- `engineering/engineering-api-platform-engineer.md` — API gateways & platforms
- `engineering/engineering-rag-pipeline-engineer.md` — Production RAG pipelines
- `engineering/engineering-llm-post-training-engineer.md` — Post-training stack (SFT/DPO/GRPO/RLVR)
- `engineering/engineering-data-visualization-engineer.md` — Perceptually honest data viz
- `security/security-architect.md` — Threat modeling, secure-by-design
- `security/security-appsec-engineer.md` — SDLC security, SAST/DAST, secure code review
- `testing/testing-reality-checker.md` — Evidence-based certification, quality gates
- `testing/testing-test-automation-engineer.md` — Playwright/Cypress E2E, flake elimination
- `specialized/lsp-index-engineer.md` — Language Server Protocol, code intelligence
- `specialized/workflow-architect.md` — Workflow discovery, mapping, and specification
- `specialized/codebase-archaeologist.md` — Multi-tool codebase drift audits
- `specialized/master-plan-architect.md` — Architectural teaching, red-team plan critique
- `specialized/civil-engineer.md` — Structural analysis, geotechnical design, global building codes
**Use Cases:**
- `github-autodiscovery`: Find libraries, CI/CD templates, infrastructure repos, codegen tools
- `specialist-builder`: Scaffold new engineering sub-specialists (platform, product, CS, referral-tech)
- `multi-agent-orchestration`: Coordinate product, platform, customer success, referral tech agents

### Operations
**Core Skills:** `deck-builder`, `github-autodiscovery`
**Agency-Agents Skills:**
- `specialized/operations-manager.md` — Lean/Six Sigma operations
- `specialized/supply-chain-strategist.md` — Supply chain management, procurement strategy
- `specialized/ma-integration-manager.md` — Post-merger integration
- `specialized/business-strategist.md` — Management-consulting strategy
- `specialized/change-management-consultant.md` — ADKAR/Kotter/Prosci change
- `support/support-infrastructure-maintainer.md` — System reliability, performance optimization
- `project-management/project-management-project-shepherd.md` — Cross-functional coordination, timeline management
- `project-management/project-management-studio-operations.md` — Day-to-day efficiency, process optimization
- `project-management/project-management-experiment-tracker.md` — A/B tests, hypothesis validation
- `testing/testing-workflow-optimizer.md` — Process analysis, workflow improvement
- `specialized/automation-governance-architect.md` — Automation governance, n8n, workflow auditing
**Use Cases:**
- `deck-builder`: Operations reviews, supply chain decks, vendor assessments, onboarding docs
- `github-autodiscovery`: Supply chain tools, procurement automation, workflow orchestration repos

### Legal
**Core Skills:** `deck-builder`, `github-autodiscovery`
**Agency-Agents Skills:**
- `specialized/legal-document-review.md` — Contract review, risk flagging, version comparison
- `specialized/legal-client-intake.md` — Prospect qualification, conflict screening, consultation scheduling
- `specialized/legal-billing-time-tracking.md` — Time capture, billing narratives, IOLTA compliance
- `specialized/fedramp-rmf-compliance.md` — Federal cloud authorization (ATO)
- `specialized/esg-sustainability-officer.md` — ESG programs & disclosure
- `security/security-compliance-auditor.md` — SOC 2, ISO 27001, HIPAA, PCI-DSS
- `specialized/data-privacy-officer.md` — GDPR/CCPA privacy compliance
- `specialized/compliance-auditor.md` — SOC 2, ISO 27001, HIPAA, PCI-DSS
- `support/support-legal-compliance-checker.md` — Compliance, regulations, legal review
- `specialized/government-digital-presales-consultant.md` — China ToG presales, digital transformation
**Use Cases:**
- `deck-builder`: Compliance reports, risk assessments, contract summaries, regulatory decks
- `github-autodiscovery`: Contract management repos, compliance automation, policy-as-code tools

### People & Comms
**Core Skills:** `deck-builder`, `github-autodiscovery`
**Agency-Agents Skills:**
- `specialized/recruitment-specialist.md` — Talent acquisition, recruiting operations
- `specialized/hr-onboarding.md` — Pre-boarding, compliance, benefits enrollment, 30-60-90 day plans
- `specialized/organizational-psychologist.md` — Team dynamics & culture health
- `specialized/change-management-consultant.md` — ADKAR/Kotter/Prosci change
- `specialized/customer-success-manager.md` — Onboarding, health & retention
- `specialized/corporate-training-designer.md` — Enterprise training, curriculum development
- `specialized/developer-advocate.md` — Community building, DX, developer content
- `support/support-support-responder.md` — Customer service, issue resolution
- `specialized/customer-service.md` — Omnichannel support, complaint handling, retention
- `marketing/marketing-pr-communications-manager.md` — PR, media relations & crisis comms
**Use Cases:**
- `deck-builder`: HR reviews, org design decks, internal comms, public affairs materials
- `github-autodiscovery`: HRIS integrations, comms tools, culture survey platforms

### AI Intelligence (Technology Platform)
**Core Skills:** `github-autodiscovery`, `specialist-builder`, `multi-agent-orchestration`
**Agency-Agents Skills:**
- `engineering/engineering-ai-engineer.md` — ML models, deployment, AI integration
- `engineering/engineering-rag-pipeline-engineer.md` — Production RAG pipelines
- `engineering/engineering-llm-post-training-engineer.md` — Post-training stack (SFT/DPO/GRPO/RLVR)
- `engineering/engineering-multi-agent-systems-architect.md` — Multi-agent pipeline design & governance
- `engineering/engineering-ai-data-remediation-engineer.md` — Self-healing pipelines, air-gapped SLMs, semantic clustering
- `engineering/engineering-prompt-engineer.md` — LLM prompt design & optimization
- `specialized/agentic-identity-trust.md` — Agent identity, authentication, trust verification
- `specialized/identity-graph-operator.md` — Shared identity resolution for multi-agent systems
- `specialized/mcp-builder.md` — Model Context Protocol servers
- `specialized/agents-orchestrator.md` — Multi-agent coordination, workflow management
- `specialized/model-qa-specialist.md` — ML audits, feature analysis, interpretability
- `specialized/zk-steward.md` — Knowledge management, Zettelkasten, notes
- `specialized/document-generator.md` — PDF, PPTX, DOCX, XLSX generation from code
- `specialized/strategy-duel-agent.md` — Game theory & the 36 stratagems
- `security/security-ai-generated-code-auditor.md` — Security review of AI/vibe-coded apps
- `security/security-secrets-credential-engineer.md` — Secrets & credential lifecycle
- `specialized/data-privacy-officer.md` — GDPR/CCPA privacy compliance
**Use Cases:**
- `github-autodiscovery`: AI/ML model repos, governance tooling, InfoSec frameworks, identity providers
- `specialist-builder`: Scaffold AI governance, model ops, InfoSec, identity sub-specialists
- `multi-agent-orchestration`: Coordinate AI strategy, models, governance, InfoSec, identity, tools agents

---

## Skill Loading at Runtime

Each department agent loads its assigned skills via the agent config:

```yaml
# kojiki/specialists/finance-accounting/config.yaml
skills:
  - deck-builder
  - github-autodiscovery
```

The skill loader in `kojiki/core/__init__.py` reads this config and makes the skill's tools, prompts, and schemas available to the agent.

---

## Adding a New Skill

1. Add skill to `skills/<skill-name>/` with `SKILL.md`
2. Update this registry with the skill description
3. Assign to departments in the table above
4. Add to department configs in `kojiki/specialists/<dept>/config.yaml`

---

## References

- `references/skill-loading.md` - How skills are loaded at runtime
- `references/department-configs.md` - Department config schema
- `references/sub-specialist-patterns.md` - Sub-specialist creation, delegation, handoffs, Mycelium signals, SENTINEL keys, LLM config
- `templates/skill-assignment.md` - Template for new skill assignments