# Contributing

## Ground rules
1. **Every decision that affects security, portability, pedagogy, evidence integrity or cost gets an ADR** (`docs/adr/`, use `0000-template.md`).
2. **Evidence is generated, never hand-edited.** Change the generator, regenerate, and commit both. Tests fail if committed evidence differs from generator output.
3. **No instructor material here.** Answer keys, live generators, rosters and secrets belong in the private `cyberlab-instructor` repository. CI scans for leaks.
4. **Label test status honestly.** Every README or guide states where and when it was tested, or `UNTESTED`.
5. **Do not weaken the security baseline.** Policy tests enforce non-root, `cap_drop: ALL`, `no-new-privileges`, read-only root, limits and network rules.

## Local checks (maintainers)
```bash
pip install pytest pytest-cov pyyaml ruff
(cd platform/lib && python3 -m pytest)                 # library
python3 -m pytest labs/*/tests tests                   # evidence, policy, docs, leaks
ruff check --config platform/lib/pyproject.toml platform/lib labs tests
docker build -f platform/images/base/Dockerfile -t local/cyberlab-base:dev platform
CYBERLAB_REGISTRY=local CYBERLAB_VERSION=dev labs/lab0-orientation/tests/integration.sh
```

## Adding a lab
Copy the structure of `labs/lab0-orientation/` (compose.yaml extending the baseline, `lab.yaml`, `docs/student-guide.md` with the 16 required sections, `tests/`). The policy and guide tests pick up new labs automatically.
