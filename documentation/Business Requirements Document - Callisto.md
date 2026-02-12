# Callisto - Business Goals

**Purpose:** Standardized platform for rapid agent PoC development

## Problem
- Repetitive infrastructure setup for each PoC
- Inconsistent tooling across projects
- No easy way to simulate multi-party conversations
- Hard to compare different LLM approaches

## Solution
Dockerized multi-agent platform with:
- Standardized agent infrastructure (LLM, vector DB, RAG)
- Dynamic scenario creation via LLM wizards
- Autonomous + human-in-loop simulation modes
- 100% local execution

## Success Metrics
- Setup time: < 15 minutes from clone to running
- Scenario creation: < 5 minutes
- Test 10+ variations in one day
- 80% code reuse across PoCs

## Use Cases

**UC1: Simulate B2B Conversation**  
Test AI sales agent against simulated client, analyze sentiment

**UC2: Practice Client Interaction**  
Participate as human with AI-generated client agent

**UC3: Multi-Party Negotiation**  
Simulate 4-way enterprise deal (tech + legal stakeholders)

**UC4: Model Comparison**  
Run same scenario with different LLMs, compare outcomes

## Core Features (Alpha)

- Dynamic scenario creation (LLM-powered agent generation)
- Multi-tenant RAG (company-specific knowledge bases)
- Agent orchestration (2-6 agents, round-robin turns)
- Real-time sentiment analysis
- Conversation persistence (Weaviate + JSON)
- Document ingestion CLI

## Constraints
- Local resources only (no cloud)
- Budget: $0
- Timeline: 2-3 weeks
- Models that fit in 16GB RAM

## Out of Scope (Alpha)
- Production deployment
- Multi-modal agents (text only)
- External system integrations
- Advanced observability (Phoenix, MLflow)
