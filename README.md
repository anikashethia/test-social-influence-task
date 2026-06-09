# Social Influence Task

Artwork rating task adapted from Welborn et al. (2016). Measures whether felt
social connection with an AI agent modulates social influence susceptibility.

Runs **after** the social connection task in the same lab session. Participants
rate artworks before (Phase 1) and after (Phase 2) seeing each agent's rating.
Influence is operationalized as the shift toward the agent's rating, normalised
by the maximum possible shift.

## Structure

```
social-influence-task/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes
│   │   ├── models.py        # SQLAlchemy models (Session, Block, Rating, Event)
│   │   ├── db.py            # DB engine / session
│   │   ├── stimuli.py       # Artwork loading & artwork-condition assignment
│   │   ├── pilot.py         # Participant counter (persistent)
│   │   └── stimuli/
│   │       ├── artworks.json       # 50 artwork stimulus definitions
│   │       └── agent_ratings.json  # Pre-generated agent ratings per artwork (add before running)
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx          # Entry point — routes to PilotApp or dev App
│   │   ├── App.tsx           # Dev landing screen
│   │   ├── PilotApp.tsx      # Prolific participant orchestrator
│   │   ├── timeline.ts       # jsPsych timeline (Phase 1 + Phase 2)
│   │   ├── api.ts            # API client
│   │   └── components/
│   │       └── TimelineRunner.tsx
│   ├── index.html
│   └── package.json
└── scripts/
    └── csv_to_artworks.py    # Convert stimulus CSV → artworks.json
```

## Task Design

**Phase 1 — Baseline rating** (~7 min)
- 50 artworks rated on a 0–100 continuous slider
- No agent information shown

**Phase 2 — Influence task** (~15 min)
- Same 50 artworks, randomly interleaved across agent conditions
- Trial structure per artwork:
  1. Artwork + agent rating reveal (4 s)
  2. Participant re-rates on 0–100 slider (self-paced, ≤8 s)
  3. ITI fixation cross (2–4 s jittered)

**12 conditions:**
- 6 named agents: Alex, Sam, Casey, Jordan, Morgan, Riley
- 6 RNG controls: RNG_1 through RNG_6 (displayed as "Another user")

Each RNG condition uses a different fixed seed so different RNG conditions
produce different ratings for the same artwork, but the same rating across
participants.

**Counterbalancing**
- Each artwork appears in exactly one condition per participant
- Condition assignment: `(artwork_id − 1 + participant_index) mod 12`
- Every 12 participants = 1 complete rotation
- 50 artworks / 12 conditions → conditions 0–1 get 5 artworks, rest get 4

**Influence score (computed at analysis time)**
```
Δ = phase2_rating − phase1_rating
normalised_influence = Δ / |agent_rating − phase1_rating|
```
Values: 0 = no influence, 1 = full conformity, negative = reactance.

## Setup

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env: add PROLIFIC_COMPLETION_URL
uv run fastapi dev
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5174 (to avoid port conflict with social
connection task on 5173).

## Before Running Participants

### 1. Populate artworks.json

Use the conversion script to generate artworks.json from the stimulus CSV:

```bash
python scripts/csv_to_artworks.py path/to/stimulus_list.csv --n 50 --out backend/app/stimuli/artworks.json
```

Arguments:
- `csv_path` (positional): path to the stimulus CSV
- `--n`: number of artworks to include (default: 50)
- `--out`: output JSON path (default: `backend/app/stimuli/artworks.json`)

The CSV should have columns: ID, Title, Artist, Year, Medium,
Style / Movement, WikiArt URL, Valence Category, Familiarity Risk.

### 2. Add agent_ratings.json

Create `backend/app/stimuli/agent_ratings.json` with pre-generated agent
ratings for each artwork. Format:

```json
{
  "Alex":   {"1": 72, "2": 45, "3": 68, ...},
  "Sam":    {"1": 60, "2": 38, "3": 55, ...},
  "Casey":  {"1": 65, "2": 50, "3": 60, ...},
  "Jordan": {"1": 58, "2": 42, "3": 52, ...},
  "Morgan": {"1": 70, "2": 48, "3": 62, ...},
  "Riley":  {"1": 55, "2": 40, "3": 58, ...}
}
```

RNG ratings are generated at runtime from fixed seeds — no entry needed.
Without this file, the backend uses deterministic placeholder ratings.

### 3. Image Hosting

Download images from WikiArt and host them. Options:
- **Local**: place in `frontend/public/artworks/1.jpg` and set
  `image_url` to `/artworks/1.jpg`
- **CDN**: upload to S3, Cloudflare R2, or similar and use full URL
- **Dev testing**: leave `image_url` blank — the frontend shows a placeholder

## Prolific Study URL

```
https://yourstudy.com/?mode=pilot&PROLIFIC_PID={{%PROLIFIC_PID%}}&identities=Alex,Sam,Casey,Jordan,Morgan,Riley&sc_session_id=<id>
```

- `identities`: comma-separated agent names from the social connection task,
  so Phase 2 labels match the agents the participant already interacted with.
- `sc_session_id`: session ID from the social connection task, for cross-task
  data linkage.

## Data

All data is stored in SQLite (`social_influence.db`). Key tables:

| Table    | Contents |
|----------|----------|
| sessions | One row per participant visit (includes `sc_session_id` for cross-task linkage) |
| blocks   | One per phase (phase=1 baseline, phase=2 influence) |
| ratings  | Every artwork rating with timing and `is_rng` flag |
| events   | jsPsych timeline events with ms timestamps |

Export ratings for analysis:
```sql
SELECT
  s.participant_id,
  s.condition_order,
  s.sc_session_id,
  r.artwork_id,
  b.phase,
  r.rating,
  r.agent_condition,
  r.agent_rating,
  r.is_rng,
  r.rating_rt_ms,
  r.trial_index
FROM ratings r
JOIN blocks b ON r.block_id = b.id
JOIN sessions s ON b.session_id = s.id
ORDER BY s.participant_id, b.phase, r.trial_index;
```
