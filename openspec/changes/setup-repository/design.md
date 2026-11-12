# Design: Set up repository and source documents

## Context

Node.js is not installed on the workstation, so the OpenSpec CLI (`@fission-ai/openspec`) cannot run.
The final deliverable is a public GitHub repository, so where the source documents end up matters.

## Decisions

Decided on 2026-11-12.

### D1: Write OpenSpec by hand instead of installing the CLI

- Options: (a) write the standard layout by hand; (b) install Node.js and the OpenSpec CLI.
- Chosen: (a). The project stays Python-only, and the files remain compatible with the CLI if it is added later.

### D2: Keep source documents local only

- Options: (a) commit the Markdown only; (b) commit the Markdown and the PDFs; (c) keep the PDFs locally but gitignored.
- Chosen: gitignore both the PDFs and the Markdown transcriptions (`docs/source/`).
- Consequence: no public deliverable may depend on a reviewer reading the source documents.

### D3: Verbatim transcription, observations kept separately

- Options: (a) verbatim, with notes in a separate document; (b) verbatim, with inline QA notes.
- Chosen: (a). The transcriptions stay a reliable copy of the source, and spec inconsistencies go into
  a separate OpenSpec document.

### D4: Initialize git and make an initial commit

- Chosen: `git init -b main` and one initial commit of the setup.

## Observations to carry forward (not yet acted on)

Spotted during transcription. They will go into a separate spec review:

- Minimum stake is €1.00 in §3 Business Rules and the §4.4 copy, but €1.01 in §4.1 Validation Rules.
- §2.1 asks for a "kickoff date/time label", but the API field `kickoffDate` is `YYYY-MM-DD` (date only).
- §2.1 states the "new selection replaces previous" requirement more than once.
- §2.2 says the bet slip "shows one active selection at a time", yet it also has "Remove All" and a per-selection `x`.
- Odds from 1.01 to 1000.00 is a business rule, but no validation rule or API error covers it.
- Spec §2.4 lists "Selection" on the receipt, but the glossary's Bet Receipt description leaves it out.
