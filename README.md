# Job Copilot

Tailors my CV to a job posting using only things I've actually done, then checks every claim and tells me where I fall short.

## Why I built it

Tailoring my CV to every posting by hand took forever. I wanted it faster, but not by stretching the truth. So this tool can only say what's in my evidence file, and it has to tell me plainly when a posting asks for something I don't have.

## What it does

You give it a posting as a text file, and it:

1. Pulls out the requirements a hiring manager would screen on.
2. Searches my evidence bank (`data/evidence.yaml`, one fact per item) for anything that backs each one.
3. Drafts a summary and bullets, each citing the evidence ids it relies on.
4. Audits every claim. Claude judges whether the cited evidence supports it, and a separate check makes sure every number in the claim is in that evidence. If they disagree, the number check wins.
5. Writes a report to `outputs/` with an honesty score, a verdict per bullet, and the gaps.

What I'm proudest of is that I can measure honesty instead of eyeballing it. `evals/run_evals.py` scores how many claims are fully supported, whether it admits the gaps I know are there, and whether anything I've banned slipped in.

Retrieval was the tricky part. With a small evidence bank, search always finds *something*, so I added a distance cutoff that drops weak matches and lets the drafter see "no evidence" instead.

## Tech stack

- Python 3.11
- Claude API for extraction, drafting, and judging. Every call returns JSON, so the code can check each step.
- ChromaDB, in memory. It rebuilds the index each run, which is fine for a few hundred facts and means no database to manage.
- YAML for the evidence bank, since it's the one file I edit by hand.
- A plain regex for the number check, so one part of the audit doesn't rely on an AI.

## What's next

Turn it into an agent: give Claude tools (search evidence, check a claim) and let it rewrite any bullet the verifier rejects until it passes.

## Running it

    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env    # then put your Anthropic API key in .env
    python main.py data/postings/sample_data_manager.txt

The first run downloads a small embedding model for Chroma, one time only. Each run costs a few cents. The model defaults to Claude Sonnet, and you can change it with `COPILOT_MODEL` in `.env`. To use it yourself, replace `data/evidence.yaml` with your own facts.

To run the evals:

    python -m evals.run_evals
