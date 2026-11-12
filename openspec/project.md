# Project Context

## Purpose

Take-home assignment for a Senior Test Automation Engineer role that includes some manual testing.
The subject under test is a simulated sports-betting web app ("Single Bet Placement").

Deliverables, all in a public GitHub repository:

1. A test plan of 5 or 6 prioritized scenarios (its own `.md` file)
2. Execution results and bug reports for the top 3 scenarios plus exploratory checks (its own `.md` file)
3. An automation framework with 2 tests: one E2E UI test and one API test
4. A strategy and recommendations note (its own `.md` file)

## How work is recorded

- Every step is an OpenSpec change under `openspec/changes/`.
- Every business decision is logged in that change's `design.md`, with the options considered and the outcome.

## Tech Stack

Required by the assignment:

- Python 3
- Selenium WebDriver with pytest (UI)
- `requests` (API)
- Latest desktop Chrome

Additional tooling: _not yet decided_.

## Project Conventions

### OpenSpec

- OpenSpec is written by hand in the standard layout. The CLI is not installed, and Node.js is not a project dependency.
- `openspec/specs/` holds the current truth (capabilities as built).
- `openspec/changes/<change-id>/` holds one folder per step: `proposal.md`, `tasks.md`, an optional
  `design.md`, and spec deltas under `specs/<capability>/spec.md`.

### Code Style, Architecture, Testing Strategy, Git Workflow

_Not yet decided._

## Domain Context

The source documents are local only (gitignored, not published):

- `docs/source/feature-specification.md`: the Single Bet Placement feature specification
- `docs/source/take-home-task.md`: the assignment brief, including the betting-domain glossary

## Important Constraints

- The source documents are not published, so public artifacts must make sense without them.
- The transcriptions are verbatim. Spec inconsistencies are recorded separately and never "fixed" in the source.

## External Dependencies

- Application under test: `https://qae-assignment-tau.vercel.app/?user-id=<user-id>`
- API docs: `/api/docs` (Swagger UI), `/api/docs?format=json` (OpenAPI)
