## ADDED Requirements

### Requirement: Local-only source documents

The repository SHALL keep the assignment source documents (PDFs and their Markdown transcriptions) in
`docs/source/` and SHALL exclude that directory from version control.

#### Scenario: Source documents are not published

- **WHEN** the repository is pushed to the public remote
- **THEN** no file under `docs/source/` is included

### Requirement: Verbatim transcriptions

Markdown transcriptions of source documents SHALL keep the original wording, including errors and
inconsistencies. QA observations SHALL be recorded in a separate document.

#### Scenario: Spec inconsistency found during transcription

- **WHEN** a contradiction is found in a source document
- **THEN** the transcription keeps the original text
- **AND** the observation is logged in OpenSpec, outside the transcription

### Requirement: Recorded steps and decisions

Every step of the assignment SHALL be recorded as an OpenSpec change. Every business decision SHALL be
logged in the change's `design.md` with the options considered and the outcome.

#### Scenario: A decision is needed

- **WHEN** a step requires a business decision
- **THEN** the options are written down before any action is taken
- **AND** the chosen option is recorded in the change's `design.md`
