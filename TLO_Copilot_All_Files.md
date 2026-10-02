# TLO — Copilot Files (Combined)

This single file contains 6 files. Before using with Copilot, split each section back into its own file at the path shown in its heading. Copilot only auto-loads `.github/copilot-instructions.md` and `.github/prompts/*.prompt.md` when they are separate files at those paths.

## Contents
- `.github/copilot-instructions.md`
- `.github/prompts/implement-slice.prompt.md`
- `.github/prompts/deploy-check.prompt.md`
- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/API.md`


<!-- ==================== FILE START: .github/copilot-instructions.md ==================== -->
# FILE: `.github/copilot-instructions.md`

# Copilot Instructions — TLO (Train Load Optimization)

## Project
Full-stack app that assigns shipping containers to railcar slots using a greedy algorithm.
- Backend: Python FastAPI, SQLAlchemy 2.0, Pydantic V2, Azure SQL (pyodbc, ODBC Driver 18), pytest
- Frontend: in the frontend folder of this repo. Read its package.json and follow the existing framework, structure and conventions. Do not switch frameworks.
- Deploy: Docker → Azure App Service. The demo MUST run on the live Azure URL, not localhost.
- Docs: `docs/PRD.md` (what to build), `docs/PLAN.md` (phases and slices), `docs/API.md` (API contract).

## Golden rule
Work on ONE slice from `docs/PLAN.md` at a time. Never build multiple slices in one task.

## Backend layout (TLO.Backend/)
```
main.py
config/database.py
models/        container, railcar, locomotive, destination, load_plan
routers/       destinations, railcars, locomotives, optimizer, load_plans
schemas/       Pydantic request/response models (the API contract)
services/      rules.py, scoring.py, optimizer.py
tests/         test_rules.py, test_optimizer.py, test_api.py
```

## Architecture rules
- Routers are thin: validate input, call a service, return a Pydantic response model. No business logic in routers.
- The optimizer has three layers:
  1. `services/rules.py` — one pure function per hard rule. Plain objects in, bool out. No DB, no I/O.
  2. `services/scoring.py` — pure scoring functions.
  3. `services/optimizer.py`
     - `plan_load(...)`: pure greedy algorithm on plain dataclasses. No DB access.
     - `run_optimizer(db, ...)`: loads from DB, calls `plan_load`, saves results, returns response.
- Use exact table and column names from `models/`. Never invent columns. If a field is missing, stop and say so.
- Existing routers already work. Extend them; do not rewrite or rename existing endpoints.
- Never hardcode credentials or URLs. Backend reads config from environment variables. Frontend reads the API base URL from its environment config. Never print or log `DATABASE_URL`.

## API contract first (frontend ↔ backend)
- `docs/API.md` is the source of truth for request/response shapes.
- For any slice touching both sides: (1) update Pydantic schemas in `schemas/` and `docs/API.md`, (2) implement backend, (3) write frontend types and API calls that match the schema field names exactly.
- If frontend and backend disagree, fix the side that differs from `docs/API.md`.
- CORS: allowed origins come from an env var (`CORS_ORIGINS`), including localhost for dev and the Azure frontend URL.

## Domain facts (do not get these wrong)
- Units are imperial: weight in **Lb**, length in **Ft**. Never convert to kg or metres.
- Container has TWO status fields:
  - `CargoStatus`: FULL / EMPTY
  - `OperationalStatus`: AVAILABLE / ASSIGNED / HOLD
  - Eligible container = FULL **and** AVAILABLE.
- `PriorityRank` 1 = highest (SAME_DAY), 10 = lowest (DEFERRED). Process in ascending rank.
- Railcar Type A = 1 well = 2 slots. Type B = 2 wells = 4 slots. Every well has one BOTTOM and one TOP slot.
- Crane fixed at (0,0). One train per optimizer run.

## The 7 hard rules (all must pass for a slot to be valid)
| Rule | Check |
|------|-------|
| R1 Weight | container weight (Lb) <= well weight limit (Lb). Equal passes. |
| R2 Length | container length (Ft) <= well max length (Ft). Equal passes. |
| R3 Bottom-before-top | TOP slot valid only if BOTTOM of the same well is already filled (including earlier in this run). |
| R4 Availability | container is FULL and AVAILABLE. |
| R5 Destination | container destination == railcar route destination. |
| R6 Railcar status | railcar is AVAILABLE. |
| R7 Positioning | vertical stacking only: slot position must be BOTTOM or TOP of a well. |

No valid slot → container goes to `unassigned` with a reason (first failing rule). Never raise an exception for this.

## Scoring
`score = utilization*w1 + priority*w2 + proximity*w3 - dig_penalty*w4`
- Every component normalised to 0–1. Weights in one config constant, no magic numbers.
- Ties broken deterministically (lowest slot ID wins).

## Testing
| Level | Where | Rules |
|-------|-------|-------|
| Unit | `tests/test_rules.py`, `tests/test_optimizer.py` | In-memory dataclasses only. No DB. |
| API | `tests/test_api.py` | FastAPI `TestClient`. Mock the DB/service layer; assert response shape matches schemas. |
| Frontend | frontend test folder | Use the project's existing test setup. Mock API calls. |
| E2E | Playwright (slice S7) | Runs against the deployed Azure URL. |

- TDD: write failing tests first, implement, run tests until ALL pass (old ones too).
- Every rule needs a pass case, a fail case and a boundary case.
- Never delete or weaken a test to make it pass.
- Tests must never write to the shared Azure SQL database.

## How you (the agent) must work
- Only modify files the current slice needs. Ask before touching anything else.
- Do not commit, push, or switch branches. Humans commit.
- Do not add dependencies without saying so; update `requirements.txt` / `package.json` if you do.
- Use type hints (Python) and explicit types (frontend). Docstrings state which rule/KPI a function implements.
- At the end of every task, list files changed and tell the human what to click through manually to verify.
- Suggest commit messages split by backend / frontend / tests, using `feat:` `fix:` `test:` `docs:` `chore:`.

<!-- ==================== FILE END: .github/copilot-instructions.md ==================== -->


<!-- ==================== FILE START: .github/prompts/implement-slice.prompt.md ==================== -->
# FILE: `.github/prompts/implement-slice.prompt.md`

---
description: Implement one TLO slice from docs/PLAN.md using TDD, backend + frontend
---
You are implementing ONE slice of the TLO project. The slice ID (for example S2) is in the user's message.

Follow these steps in order:

1. Read `docs/PLAN.md` and find that slice. Also read `docs/PRD.md`, `docs/API.md` and `.github/copilot-instructions.md`.
2. Read the backend and frontend files the slice touches, and the relevant files in `models/`.
3. Before writing code, reply with a short plan, then STOP and wait for "go":
   - API contract changes (if any)
   - backend files to change
   - frontend files to change
   - tests to add (one line each, grouped: unit / API / frontend)
   - assumptions or missing DB fields
4. Contract first: update `docs/API.md` and the Pydantic schemas if the slice changes request/response shapes.
5. Write the failing tests. Run them and show they fail.
6. Implement backend, then frontend (types and field names must match the schemas exactly).
7. Run ALL backend and frontend tests until everything passes, including older tests.
8. Finish with:
   - files changed (one line each)
   - tests added
   - assumptions or anything unclear
   - manual check: exact steps the human should click through in the running app
   - suggested commit messages, split by backend / frontend / tests so different owners can commit their own part

Rules:
- Only this slice. Do not start the next one.
- Only touch files the slice needs. Ask before touching anything else.
- Do not commit, push, or switch branches.
- If a column you need is not in `models/`, stop and ask. Do not invent it.
- Never delete or weaken an existing test to make it pass.
- Tests must never write to the shared Azure SQL database.

<!-- ==================== FILE END: .github/prompts/implement-slice.prompt.md ==================== -->


<!-- ==================== FILE START: .github/prompts/deploy-check.prompt.md ==================== -->
# FILE: `.github/prompts/deploy-check.prompt.md`

---
description: Prepare and verify TLO for Docker + Azure App Service deployment
---
Review the repo for Azure deployment readiness. Do NOT deploy anything yourself and do not change Azure settings. Check and fix files only where needed, then report.

Check:
1. Backend `Dockerfile` installs Microsoft ODBC Driver 18 for SQL Server (`msodbcsql18`) and `unixodbc`. Without it the app fails with IM002 on Azure.
2. The app listens on `0.0.0.0` and the port is documented (Azure needs `WEBSITES_PORT` to match).
3. All config comes from environment variables: `DATABASE_URL`, `CORS_ORIGINS`, `SECRET_KEY`. No secrets in code, Dockerfile or committed files. `.env` is in `.gitignore`.
4. CORS reads allowed origins from `CORS_ORIGINS`.
5. Frontend reads the backend base URL from environment config, not a hardcoded localhost.
6. `/health` returns quickly without touching the DB.
7. `requirements.txt` / `package.json` contain everything needed.

Then output a checklist for the human to do in the Azure portal:
- App Service configuration: env vars to set (names only, never values)
- `WEBSITES_PORT` value
- Azure SQL firewall: allow Azure services / App Service outbound IPs
- CORS origin to add once the frontend URL is known
- Smoke test steps: `/health`, `/destinations`, then the full 3-step flow

<!-- ==================== FILE END: .github/prompts/deploy-check.prompt.md ==================== -->


<!-- ==================== FILE START: docs/PRD.md ==================== -->
# FILE: `docs/PRD.md`

# PRD — Train Load Optimization (TLO)

## 1. Problem
Rail yard planners assign containers to railcar slots by hand. This is slow, error-prone and rarely optimal:
railcars leave with empty slots, cranes travel more than needed, weight limits get violated, decisions vary by planner, and urgent cargo can be left behind.

## 2. Goal
A web app that generates a valid, explainable load plan for one train in seconds, using a greedy algorithm that obeys 7 hard safety/business rules and then picks the best slot by score.

## 3. Users
- **Planner** — selects a destination and railcars, runs the optimizer, reviews the plan and KPIs.
- **Admin** — manages master data (containers, railcars, locomotives). Not a demo priority.

## 4. User flow
1. **Select train** — choose destination from a dropdown (from DB). Table of available railcars for that destination, all checked by default; user can uncheck.
2. **Review & generate** — show the 7 hard rules. "Generate Plan" calls `POST /optimize`.
3. **Results** — KPI cards + assignments as a table and as a railcar diagram. Unassigned containers listed with reasons.

## 5. Hard rules (what is ALLOWED)
R1 Weight, R2 Length, R3 Bottom-before-top, R4 Availability, R5 Destination, R6 Railcar status, R7 Positioning.
Exact definitions: `.github/copilot-instructions.md`.

## 6. Greedy algorithm (what is BEST)
```
eligible containers sorted by PriorityRank ascending
for each container:
    valid_slots = slots passing all 7 rules
    if none: add to unassigned with reason
    else: assign to highest-scoring slot, mark slot occupied
save LoadPlanHeader, LoadPlanLine, LoadPlanKPI
```
Score = utilization×w1 + priority×w2 + proximity×w3 − dig_penalty×w4 (normalised 0–1).

Why greedy: fast, transparent, explainable to business users. MILP too slow for interactive use, CP too complex, DVRP overkill for one train.

## 7. KPIs
- Slot utilization = assigned slots / total slots on selected railcars
- Containers loaded
- Containers unassigned (eligible, but no valid slot)
- Containers set aside (excluded before the run, e.g. EMPTY or HOLD)
- Crane distance (from crane at (0,0))

## 8. Data facts
Imperial units (Lb, Ft). Two container status fields. PriorityRank 1 = highest. Type A railcar = 1 well, Type B = 2 wells, each well = BOTTOM + TOP. Synthetic seed data; a reset script restores the initial state.

## 9. Assumptions
Crane fixed at (0,0). One train per run. Only FULL containers eligible. No live yard integration.

## 10. Out of scope
Multiple trains per run, live yard feeds, re-optimising a saved plan, admin CRUD polish.

## 11. Open questions (decide before Slice 5)
1. **Scoring reality check:** `priority` and container-location `proximity` are the same for every slot a given container could take, so they do not change which slot is chosen. Only slot-dependent terms (utilization, slot-based proximity, dig penalty) affect the choice. Decide: should proximity measure distance to the railcar/slot position, and what does dig penalty measure in our data?
2. Is R1 per container, or the combined weight of BOTTOM + TOP in a well?
3. Exact definition of "set aside" for the KPI.
4. Crane distance: computed from which coordinates in our DB?

## 12. Demo success criteria (Oct 9)
- Runs on the live Azure URL
- Full flow (Step 1 → 3) works for any destination
- Zero rule violations in the generated plan
- Every team member can explain their own part

<!-- ==================== FILE END: docs/PRD.md ==================== -->


<!-- ==================== FILE START: docs/PLAN.md ==================== -->
# FILE: `docs/PLAN.md`

# TLO Build Plan — Phases and Slices

## Phases
| Phase | What | When |
|-------|------|------|
| 0. Setup | Repo has `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md`, `docs/PRD.md`, `docs/PLAN.md`, `docs/API.md`. Open the REPO ROOT in VS Code (backend + frontend). Confirm `pytest` and frontend tests run. | Oct 2 |
| 1. PRD | Team reviews `docs/PRD.md`; resolve open questions. | Oct 2–3 |
| 2. Slices | Vertical slices below. Each is end to end and leaves the app working. | Done |
| 3. Build (human-in-the-loop) | Per slice: `/implement-slice S#` → approve plan → tests red → green → manual click-through → owner commits → PR to `cicd`. | Oct 3–8 |
| 4. Deploy & harden | `/deploy-check` on S1, redeploy after every slice. Fill test gaps, rehearse demo on Azure URL. | Oct 3 onward |

## Loop for every slice
1. Owner + license holder open Copilot Chat in **Agent** mode.
2. `/implement-slice S#`. Agent proposes plan → owner checks → reply "go".
3. Agent updates `docs/API.md` + schemas if needed, writes failing tests, implements, runs tests until green.
4. Run backend + frontend locally. Do the 3-step flow by hand.
5. Owner reads every changed line and can explain it.
6. Owner commits from their own branch. PR → Jatin reviews → merge to `cicd`.
7. Redeploy to Azure, click through, run reset script.

Never commit directly to `cicd`. Commit after every slice, never in one batch at the end.

---

## S1 — Walking skeleton (end to end, deployed)
**Target:** Oct 3 | **Owners:** Jatin (optimizer), Samikshya (save to DB), Jyotiraditya (UI), Aneesh (deploy)

Backend
- `schemas/optimize.py`: request/response per `docs/API.md` (no score, no kpis yet)
- `services/rules.py`: `r4_availability`, `r5_destination`
- `services/optimizer.py`: `plan_load` assigns eligible containers (priority order) to first free BOTTOM slot on selected railcars. `run_optimizer` saves LoadPlanHeader + LoadPlanLine, sets container `OperationalStatus`=ASSIGNED, marks slot occupied.
- `POST /optimize` wired to the service. CORS from `CORS_ORIGINS`.

Frontend
- Step 1: destination dropdown (`GET /destinations`), railcar table (`GET /railcars/{id}`), all checked
- Generate button → `POST /optimize`
- Results: plain table of assignments + unassigned list

Tests
- R4: FULL+AVAILABLE passes; EMPTY, HOLD, ASSIGNED fail
- R5: matching destination passes; different fails
- `plan_load`: rank 1 assigned before rank 5; no free slot → `unassigned` with reason, no exception
- API: `POST /optimize` returns 200 and matches schema (service mocked)
- Frontend: Generate button calls API and renders rows (API mocked)

**Done when:** a plan is generated from the Azure URL and the reset script restores the DB.

## S2 — Physical fit (R1, R2)
**Target:** Oct 4 | **Owner:** Jatin
- `r1_weight`, `r2_length` used in `plan_load`; reasons shown in UI unassigned list.
- Tests: equal to limit passes; 1 Lb / 1 Ft over fails; overweight container → `unassigned` with "R1".

## S3 — Stacking (R3, R7) and TOP slots
**Target:** Oct 5 | **Owner:** Jatin
- `r3_bottom_before_top`, `r7_positioning`; TOP slots now used.
- Tests: TOP rejected when BOTTOM empty; TOP accepted after BOTTOM filled earlier in same run; only BOTTOM/TOP allowed; Type B railcar holds 4.

## S4 — Railcar selection (R6)
**Target:** Oct 5 | **Owners:** Jatin (backend), Almaas (checkbox UI)
- `r6_railcar_status`; only `selected_railcar_ids` used; Step 2 screen lists the 7 rules.
- Tests: non-AVAILABLE railcar never used; unchecked railcars never used; zero selected → all unassigned, no crash; frontend sends only checked IDs.

## S5 — Scoring
**Target:** Oct 6 | **Owner:** Jatin | **Blocked by:** PRD open question 1
- `services/scoring.py`; `plan_load` picks max score; `score` returned in API and shown in table.
- Tests: higher-scoring slot chosen; tie → lowest slot ID; scarce capacity → rank 1 loaded, rank 10 left; components within 0–1.

## S6 — KPIs
**Target:** Oct 7 | **Owners:** Samikshya (save KPIs), Almaas (KPI cards)
- Compute + save LoadPlanKPI; `kpis` in `/optimize` response; `GET /loadplans/{id}/kpis`; KPI cards on results page.
- Tests: utilization = assigned slots / total selected slots; loaded + unassigned = total eligible; saved KPIs == returned KPIs.

## S7 — Diagram, polish, E2E
**Target:** Oct 8 | **Owners:** Jyotiraditya (diagram), Almaas (loading/error states), Aneesh + Argha (E2E, final deploy)
- Railcar diagram: each well shows BOTTOM/TOP with container code.
- Loading and error states on all 3 steps.
- One Playwright test: full 3-step flow on the Azure URL.

**Done when:** full demo rehearsal works on Azure after running the reset script.

<!-- ==================== FILE END: docs/PLAN.md ==================== -->


<!-- ==================== FILE START: docs/API.md ==================== -->
# FILE: `docs/API.md`

# TLO API Contract

Source of truth for frontend ↔ backend. Pydantic models in `TLO.Backend/schemas/` must match this file.
Existing endpoints keep their current paths. If an existing response differs from this file, align this file to the real response first, then keep both in sync.

## Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Liveness check |
| GET | /destinations | Destination dropdown |
| GET | /railcars/{destination_id} | Railcars available for a destination |
| GET | /locomotives/{destination_id} | Locomotives for a destination |
| POST | /optimize | Run greedy optimizer, save and return plan |
| GET | /loadplans | List plans |
| GET | /loadplans/{plan_id} | One plan with assignments |
| GET | /loadplans/{plan_id}/kpis | KPIs for a plan |

## POST /optimize

### Request
```json
{
  "destination_id": 1,
  "locomotive_id": 10,
  "selected_railcar_ids": [1, 2, 5]
}
```

### Response
```json
{
  "plan_id": 12,
  "assignments": [
    {
      "container_id": 1001,
      "container_code": "CON-1001",
      "priority_rank": 1,
      "railcar_id": 2,
      "well_id": 3,
      "slot_id": 5,
      "slot_position": "BOTTOM",
      "score": 0.82
    }
  ],
  "unassigned": [
    { "container_id": 1044, "container_code": "CON-1044", "reason": "R1: exceeds well weight limit" }
  ],
  "kpis": {
    "slot_utilization": 0.75,
    "containers_loaded": 18,
    "containers_unassigned": 3,
    "containers_set_aside": 4,
    "crane_distance": 152.4
  }
}
```

Notes:
- `kpis` may be omitted until slice S6.
- `score` may be null until slice S5.
- Validation errors return HTTP 422 (FastAPI default). Empty selection is NOT an error: everything goes to `unassigned`.

<!-- ==================== FILE END: docs/API.md ==================== -->
