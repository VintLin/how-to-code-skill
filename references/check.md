# Check Protocol

Run the six-gate check before completion:

1. format
2. lint
3. build
4. related tests
5. regression tests
6. semantic impact check (when protocol/constants changed)

## Rules

- Do not push fixes blindly after CI failure; reproduce locally first.
- Do not skip semantic impact checks for naming/protocol/serialization changes.
- Capture command evidence for validation sections.
