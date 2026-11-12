# Change: Automation framework design (Part B)

## Why

Part B asks for a small, well-structured automation project with two high-value tests, and the framework
is graded more than the tests. The design is settled before any code is written.

## What Changes

- Define the framework: layout, modules and function signatures, fixtures, dependencies, tool config,
  pre-commit, CI and the README outline (see `design.md`).
- Automate TC-01 (UI) and TC-03 (API), with a structure that TC-02, TC-04, TC-05 and TC-06 fit into later.

## Impact

- Affected specs: `automation-framework` (new)
- Files created at build time: `pyproject.toml`, `poetry.lock`, `.pre-commit-config.yaml`, `.env.example`,
  `README.md`, `.github/workflows/tests.yml`, `src/betting_qa/**`, `tests/**`; `.gitignore` is extended
