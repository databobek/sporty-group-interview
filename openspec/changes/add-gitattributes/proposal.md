# Change: Normalize line endings

## Why

Git on Windows warned that LF files would be converted to CRLF. The repository will be public and cloned
on other operating systems, so line endings should be the same everywhere.

## What Changes

- Add `.gitattributes` with `* text=auto eol=lf`, and mark images and PDFs as `binary`.
- Renormalize the tracked files.

## Impact

- Affected specs: `repository`
- Affected files: `.gitattributes`
