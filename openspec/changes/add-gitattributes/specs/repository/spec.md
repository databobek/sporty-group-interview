## ADDED Requirements

### Requirement: Normalized line endings

The repository SHALL store and check out text files with LF line endings on every OS, and SHALL treat image
and PDF files as binary.

#### Scenario: Clone on Windows

- **WHEN** the repository is cloned and its files are staged on Windows
- **THEN** git shows no LF/CRLF conversion warnings
