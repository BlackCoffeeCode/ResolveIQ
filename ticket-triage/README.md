# ResolveIQ

ResolveIQ is a full-stack support workflow that classifies incoming ticket text, assigns urgency, sets a priority level, and stores results for review.

It is intentionally simple and explainable:
- FastAPI + SQLAlchemy + PostgreSQL on the backend
- React + Vite on the frontend
- Rule-based standard triage with optional backend-only OpenAI analysis

## Quick Start
From this directory:
```bash
docker compose up --build
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Architecture Overview
The standard and AI analyses are independent paths. Both use the saved ticket, but each result is stored separately.

```mermaid
flowchart TD
	User[User in browser] --> UI[React application]
	UI --> Form[Ticket form]
	UI --> StandardPanel[Standard triage panel]
	UI --> AIAnalysisPanel[AI analysis panel]
	UI --> RecentTickets[Recent tickets]

	Form -->|POST /tickets/analyze| API[FastAPI]
	API --> TicketController[Ticket controller]
	TicketController --> TicketService[Ticket service]
	TicketService --> RuleAnalyzer[Rule-based analyzer]
	RuleAnalyzer -->|standard result| TicketService
	TicketService -->|save standard result| TicketsTable[(tickets)]
TicketService -->|standard result| API
API --> StandardPanel

	UI -->|AI analysis request| API
	API --> AIController[AI analysis controller]
	AIController -->|load ticket message| TicketService
	AIController --> AIService[AI analysis service]
	AIService -->|ticket text| OpenAI[OpenAI API]
	OpenAI -->|structured response| AIService
	AIService -->|validated analysis| AIController
	AIController -->|save latest analysis| AIAnalysesTable[(ticket_ai_analyses)]
	AIController -->|AI result| API
	API --> AIAnalysisPanel

	UI -->|GET /tickets| API
TicketService -->|tickets + optional AI results| API
API --> RecentTickets
	TicketsTable ---|one-to-one| AIAnalysesTable
```

Backend responsibilities are split by layer:
- Controller: receives HTTP requests, validates payloads, returns response models
- Service: coordinates analysis + persistence and manages transaction boundaries
- Analyzer: pure heuristic engine (stateless, deterministic)
- Model: SQLAlchemy ORM mapping for storage

In short: Controller handles HTTP, Service handles persistence, Analyzer handles intelligence, Model handles DB structure.

## API Reference
- POST /tickets/analyze - Analyze a ticket and persist the result
- POST /tickets/{ticket_id}/ai-analysis - Analyze and save AI output for a ticket
- GET /tickets?limit=50 - Fetch recent analyzed tickets
- GET /health - Basic health check
- GET /docs - Swagger/OpenAPI UI

## NLP / Classification Approach
The classification engine is rule-based and fully local.

How categorization works:
- Ticket text is normalized to lowercase
- Each category gets a score based on matched keywords
- Highest score wins
- Tie-break order: Security > Billing > Technical > Account > Feature Request > Other
- If nothing matches, category falls back to Other

How urgency works:
- Urgency becomes true if any urgency keyword is present

How priority works:
1. If any P0 signal is present, priority is P0
2. Else if any P1 signal is present, priority is P1
3. Else if urgency is true and no P2 signals exist, priority is P1
4. Else if any P2 signal is present, priority is P2
5. Else if any P3 signal is present, priority is P3
6. Else default is P2

How confidence score is calculated:
- matched_keywords_in_winning_category / total_keywords_in_that_category
- clamped to [0.1, 1.0]
- rounded to 2 decimals
- if category is Other (no match), confidence is fixed at 0.1

This design keeps decisions explainable via matched signals and extracted keywords.

## Custom Rule: Security Escalation
Security is treated as a hard-override workflow.

If a ticket matches security keywords:
- category is treated as Security (or security context is detected)
- priority is forced to P0
- urgency is forced to true
- is_security_escalated is set to true

Why this is strict: security incidents (breaches, hacks, leaked data, SQL injection, unauthorized access) should not wait in normal queues. Fast escalation helps reduce blast radius and supports compliance requirements.

Example:
- "I found a SQL injection in your login page" -> Category: Security, Priority: P0, Escalated: true

## Running Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

Tip: If local Python/package compatibility is different on your machine, run tests through Docker:

```bash
docker compose run --rm backend pytest tests/ -v --tb=short
```

## Optional OpenAI Analysis

Standard triage remains local and rule-based. After a ticket is saved, AI analysis runs automatically and is saved separately as the latest AI result for that ticket. It never changes the standard triage fields. Recent Tickets shows whether an AI result is available; expand a row to view the analysis. AI analysis requires a backend OpenAI API key; without one, standard triage continues to work and the AI panel reports that AI is unavailable.

From this directory, create a local environment file and add your key:

```bash
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. The default model is `gpt-4.1-mini`; set `OPENAI_MODEL` there to use another supported model. Never put the key in frontend files or commit `.env`.

Start or rebuild the stack with `docker compose up --build`, then submit a ticket in the UI. AI analysis runs automatically after standard triage. To analyze an existing ticket directly, replace `1` below with its ticket ID:

```bash
curl -X POST http://localhost:8000/tickets/1/ai-analysis
curl http://localhost:8000/tickets?limit=50
```

The AI response includes `category`, `priority`, `summary`, `likely_cause`, `suggested_resolution`, `explanation`, and `analyzed_at`. `GET /tickets` includes the saved AI response as `ai_analysis`, or `null` until analysis succeeds. An unknown ticket ID returns `404`; missing configuration or provider outages return `503`, and an unexpected model response returns `502`. The endpoint is listed in `/docs` and `/openapi.json`. The AI results use a separate table created automatically at startup; no manual migration is needed.

## Reflection (Design Decisions, Trade-offs, Limitations, What I'd Improve)

### Design Decisions
- FastAPI was chosen for quick API development, strong validation, and OpenAPI docs out of the box.
- PostgreSQL was preferred over SQLite for production behavior and containerized consistency.
- Keyword rules are config-driven in keywords.py so updates do not require touching analyzer logic.
- Layered architecture (controller/service/analyzer) keeps responsibilities clear and testable.

### Trade-offs
- Rule-based matching is transparent and fast, but it can produce false positives in ambiguous text.
- Confidence score reflects keyword density within a category, not true model probability.
- No stemming/lemmatization means wording variants (for example, crashed vs crash) may be missed.

### Limitations
- Keyword lists require periodic maintenance as user language evolves.
- There is no learning loop from previously resolved tickets.
- Confidence is a heuristic signal, not statistically calibrated confidence.

### What I'd Improve With More Time
- Add local semantic ranking (for example TF-IDF or sentence-transformers) while keeping explainability.
- Add ticket lifecycle states (open, in-progress, resolved, closed) and editing workflows.
- Add JWT-based authentication and role-aware access.
- Introduce proper DB migrations with Alembic revision flow.
- Add pagination/filtering for ticket history APIs.
- Add WebSocket push for real-time ticket updates on the dashboard.
- Add API rate limiting and abuse protection.

## Maintainer

ResolveIQ is developed and maintained by Piyush Dhakad.
