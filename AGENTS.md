# AGENTS.md: linkt-cookbook (customer-facing examples and skills)

Org conventions: `linkt-ai/master` `AGENTS.md`. This repository is not a
submodule of a project wrapper, so there is no `../AGENTS.md` to read. Query
durable knowledge before assuming: `ctl kb search "<topic>"`.

## Purpose

A public cookbook for building GTM workflows on the Linkt platform. Customers
clone it and run it in their own Claude Code session. Everything here is product
surface, not internal tooling.

| Path | Holds |
|---|---|
| `.claude/skills/` | five customer-facing skills |
| `python/01_search/` | lead discovery examples |
| `python/02_ingest/` | CSV upload and enrichment |
| `python/03_signals/` | signal monitoring |
| `python/04_advanced/` | bulk operations, exports, schedules |
| `typescript/` | placeholder, examples not written yet |
| `docs/` | skills overview and Slack setup |

Skills: `/linkt-init`, `/linkt-signals`, `/linkt-outreach`, `/linkt-schedule`,
`/linkt-status`.

## Two org rules do not apply here

- **`.mcp.json` at the repository root is correct.** The org convention against
  project-level `.mcp.json` files governs internal repositories. This file
  configures the Linkt MCP server and Slack for the customer's own session, so it
  is a shipped artefact.
- **`.claude/CLAUDE.md` is correct and is not the `@AGENTS.md` bridge.** It is
  the instruction file a customer's Claude Code reads when they open the
  cookbook. This root `AGENTS.md` is for a Linkt agent working on the cookbook.
  Keep the two separate and do not merge them.

The root `CLAUDE.md` beside this file is the ordinary one-line `@AGENTS.md`
bridge.

## V2 examples

`v2/` contains direct HTTP examples and MCP setup. The backend candidate owns `v2/examples.json`; preserve its source and digest in `v2/source.json`. Validate with the wrapper content checker and local unittest suite. V2 uses campaign/account/person identifiers and its own schemas. Legacy vocabulary below applies only to the retained V1 examples and skills.

## Legacy V1 constraints

- **Every example loads `.env` from the repository root** and reads
  `LINKT_API_KEY`. Optional: `LINKT_API_ENVIRONMENT=staging`. Slack outreach also
  needs `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID`.
- **Never commit a key.** `.claude/user-context.json` is written by `/linkt-init`,
  holds personal information, and is gitignored. Keep it that way.
- **The vocabulary is fixed.** Entity types: `company`, `person`, `job_board`,
  `school_district`, `product`. Signal strengths: `strong`, `moderate`, `weak`.
  Status values: `new`, `reviewed`, `passed`, `contacted`. Schedule frequencies:
  `daily`, `weekly`, `monthly`. Signal `score` is `0.0` to `1.0`. Use `icp_ids`,
  a list, for multi-ICP filtering.
- **Keep `.claude/CLAUDE.md` and `README.md` in step with the code.** A customer
  reads them as the contract.

## Language

Every word here reaches a customer: README prose, skill text, script comments,
and printed output. Follow Simplified Technical English. There is no marketing
register. See the Language section of `linkt-ai/master` `AGENTS.md`.
