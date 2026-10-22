# Job Search Copilot (that doesn't make things up)

Tailors a CV to a Canadian job posting using only verified evidence, then audits
every claim and reports gaps honestly.

    posting ──► extract requirements ──► retrieve evidence (RAG) ──► draft with citations
                                                                         │
                     outputs/<name>.md ◄── honesty report ◄── verify each claim (evals)

## Setup (about 15 minutes)

    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...                  # Windows: set ANTHROPIC_API_KEY=...
    python main.py data/postings/sample_data_manager.txt

Get an API key at console.anthropic.com. Each run costs a few cents.
The first run downloads a small embedding model for Chroma (one time).

## Files

| File | What it does |
|---|---|
| `data/evidence.yaml` | Your facts, one per item. The single source of truth. |
| `copilot/retrieve.py` | RAG: finds evidence relevant to each requirement |
| `copilot/tailor.py` | Extracts requirements, drafts bullets that cite evidence ids |
| `copilot/verify.py` | Honesty check: AI judge + a number check the AI can't override |
| `evals/run_evals.py` | Scores the tool across all test postings |

## Build plan

**Week 1 — Make it run.** Fill `evidence.yaml` (fix the TODOs, add 20–40 items).
Run the sample posting. Read the output critically: is anything stretched?

**Week 2 — Build the test set.** Save ~10 of your real postings into
`data/postings/` and add them to `evals/cases.yaml` with the gaps we already
identified (Fabric, Asset Bundles, 15+ years, etc.). Run `python -m evals.run_evals`
and write down your baseline numbers.

**Week 3 — Improve and measure.** Change one thing at a time (retrieval `k`,
`max_distance`, the drafting prompt) and rerun evals. Keep a table of what
changed and what moved. This table is your interview story.

**Week 4 — Add the agent.** Give Claude tools (search evidence, check a claim,
look up the company) and let it decide when to use them, rewriting any bullet the
verifier rejects until it passes.

**Weeks 5+ — Polish.** Simple web UI (Streamlit), cover letter mode, then a
LinkedIn post with your before/after eval numbers.

## The interview story

"Most AI resume tools invent experience. I built one that measures whether every
claim is backed by evidence, tested it on 20 real postings, and improved its
honesty score from X to Y."
