# Change: Set up repository and source documents

## Why

Test design needs a version-controlled workspace, a record of every step and decision (OpenSpec), and
the two PDF briefs as text that can be referenced and searched.

## What Changes

- Initialize a git repository on branch `main`.
- Add an OpenSpec structure written by hand (`openspec/project.md`, `specs/`, `changes/`).
- Copy both PDFs into `docs/source/` and transcribe them verbatim to Markdown.
- Gitignore `docs/source/` so that neither the PDFs nor the transcriptions are published.

## Impact

- Affected specs: `repository` (new capability)
- Affected files: `.gitignore`, `openspec/**`, `docs/source/**` (local only)
