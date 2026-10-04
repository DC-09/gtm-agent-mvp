# Iusful GTM Agent

## Mission
Build and operate a small GTM research system for Iusful.
The goal is quality, not volume: 20-50 evidence-backed Italian SME prospects.

## Product context
Read `docs/prd.md` first: problem and non-goals are fixed.
Read `docs/iusful_product.md` before prospecting.
Read `docs/icp.md` and `docs/scoring.md` before scoring any lead.

## Core rules
1. Never invent company facts, headcount, funding, job openings or contact details.
2. Every buying signal must have a source URL and, when possible, a date.
3. Separate observed facts from inferred legal pains.
4. Missing evidence must reduce confidence; do not fill gaps with plausible stories.
5. Prefer 20 excellent leads over 200 weak leads.
6. Do not send outreach automatically in the MVP.
7. Never commit secrets or tokens.

## Agent loop
For each objective:
1. Plan the research.
2. Inspect existing data before requesting new enrichment.
3. Identify missing fields.
4. Use the cheapest/reliable source first.
5. Re-evaluate the lead after each important finding.
6. Stop researching weak leads early.
7. Export only qualified leads to n8n/CRM.

## Verification
- After any change to lead data, run `python scripts/validate_leads.py` and show its output.
- Before exporting, run `python scripts/verify_sources.py`: export refuses leads without a fresh source check.
- Show evidence (command, output, URL); never just claim success.

## Output contract
Every qualified lead must satisfy `schemas/lead.schema.json`.
