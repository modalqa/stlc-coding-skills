# CI Integration (no GitHub Actions required)

`scripts/run_checks.py` is the whole quality and security gate. Any CI system that runs Python 3.11+ can call it. It runs:

| Step | What | Tool |
|---|---|---|
| repository | structure, skill contract, registry, adapters, versions, secret patterns, tracked sensitive files, dependency licenses | stdlib |
| tests | unit and evaluation self-tests (validator negative controls, harness, packaging, fixtures) | unittest |
| golden | validator on golden runs | stdlib |
| package | reproducible build | stdlib |
| sast | Python static security analysis | bandit |
| deps | known vulnerabilities in pinned dev tooling | pip-audit |
| secrets | secret scan of git history (or of the working tree when no git) | gitleaks |

Missing security tools **fail** the gate unless you pass `--allow-missing-tools` (meant for local use only).

## GitLab CI

```yaml
stlc-checks:
  image: python:${PYTHON}-slim
  parallel:
    matrix:
      - PYTHON: ["3.11", "3.15"]
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates
    - pip install -r requirements-dev.txt
    - curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz | tar -xz -C /usr/local/bin gitleaks
  script:
    - python scripts/run_checks.py
```

(Verify the gitleaks asset name and checksum on its release page before pinning it.)

## Jenkins (declarative)

```groovy
pipeline {
  agent { docker { image 'python:3.14-slim' } }
  stages {
    stage('STLC checks') {
      steps {
        sh 'pip install -r requirements-dev.txt'
        sh 'python scripts/run_checks.py'
      }
    }
  }
}
```

## Local pre-push hook

```bash
printf '#!/bin/sh\nexec python3 scripts/run_checks.py\n' > .git/hooks/pre-push && chmod +x .git/hooks/pre-push
```

## Recommendations

- Test the oldest (3.11) and newest (3.15) supported Python versions.
- Keep tool versions pinned. Update them through reviewed PRs, and re-run pip-audit.
- Run the gate on every merge request and on a weekly schedule, so that new CVEs in dev tooling surface.
