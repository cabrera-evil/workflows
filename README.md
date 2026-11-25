<!--

********************************************************************************

WARNING:

    DO NOT EDIT "workflows/README.md"

    IT IS PARTIALLY AUTO-GENERATED

    (based on reusable workflow files and usage examples)

********************************************************************************

-->

# Quick reference

- **Maintained by**:  
  [Douglas Cabrera](https://github.com/cabrera-evil)

- **Where to get help**:  
  [GitHub Issues](https://github.com/cabrera-evil/workflows/issues)

# What is workflows?

**workflows** is a curated collection of reusable GitHub Actions workflows designed to standardize CI/CD pipelines across multiple repositories. Each workflow is modular, version-controlled, and production-ready, making it easy to compose consistent automation logic for testing, building, deploying, and more.

These workflows follow GitHub’s [reusable workflow model](https://docs.github.com/en/actions/using-workflows/reusing-workflows) and are designed for flexibility, extensibility, and easy integration.

# How to use these workflows

In any repository where you want to reuse a workflow:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]

jobs:
  analyze:
    uses: cabrera-evil/workflows/.github/workflows/code-analysis.yaml@main
    with:
      node-version: 20
```

> Replace `code-analysis.yaml` with the workflow you want to use.
> Pin to a specific commit or tag in production environments. Internal composite references
> are `@master`; to pin, replace them in the workflows with the same tag or SHA.

# Available workflows

| Workflow File                | Purpose                                                            |
| ---------------------------- | ------------------------------------------------------------------ |
| `code-analysis.yaml`         | Run static analysis (e.g., ESLint, TypeScript, format checks)      |
| `container-analysis.yaml`    | Analyze Dockerfile or image vulnerabilities using Trivy            |
| `deploy-dokploy.yaml`        | Deploy applications to servers using Dokploy webhook               |
| `deploy-helm.yaml`           | Deploy Helm charts to Kubernetes clusters                          |
| `deploy-k8s.yaml`            | Apply raw Kubernetes manifests using `kubectl`                     |
| `deploy-vercel.yaml`         | Trigger Vercel deployment using token and team/project info        |
| `deps-analysis.yaml`         | Analyze dependencies using tools like `npm audit`, `osv-scanner`   |
| `notify-status-discord.yaml` | Send job status notifications to Discord via webhook               |
| `prisma-migrate.yaml`        | Run Prisma database migrations                                     |
| `publish-docker.yaml`        | Build and push Docker images to Docker Hub or GitHub Packages      |
| `publish-npm.yaml`           | Publish JavaScript packages to NPM registry                        |
| `register-deployment.yaml`   | Register a deployment in GitHub to be tracked in UI/metrics        |
| `semantic-release.yaml`      | Automate versioning and changelog generation with semantic-release |
| `set-deployment-status.yaml` | Mark a deployment as success/failure in GitHub                     |
| `set-environment.yaml`       | Set dynamic environment variables at runtime or per context        |

> Each workflow is self-documented via `inputs:` and `secrets:` in the YAML header.

# Composite actions

Each does one thing and is used by the deploy/migrate/notify workflows (`tailscale: true`, `infisical: true`).
Composite actions cannot read `vars` or `secrets`, so the workflows pass them in as inputs.

| Action                          | Responsibility                                                              |
| ------------------------------- | --------------------------------------------------------------------------- |
| `.github/actions/tailscale`     | Join the tailnet as an ephemeral node (keyless OIDC; OAuth/authkey fallback) |
| `.github/actions/infisical`     | Fetch secrets as masked env vars, or as a dotenv file (OIDC; Universal Auth fallback) |
| `.github/actions/secrets-convert` | Turn the Infisical dotenv file into Helm values or a Kubernetes Secret (`convert.py`, tested by `test_convert.py`) |

# Setup (once per org)

**Actions variables** (org level; no secrets needed for the keyless flow):
`TS_CLIENT_ID`, `TS_AUDIENCE`, `TS_TAGS` (e.g. `tag:ci`), `INFISICAL_DOMAIN`, `INFISICAL_PROJECT_SLUG`, `INFISICAL_IDENTITY_ID`.

**Tailscale**: create a federated identity (workload identity federation) with GitHub as issuer, a subject
pattern for your repos and the tag(s) above; copy its client ID and audience into the variables.

**Infisical**: create a Machine Identity with OIDC Auth (issuer `https://token.actions.githubusercontent.com`,
subject pattern for your repos), grant it read access to the project and paths, and put its ID in `INFISICAL_IDENTITY_ID`.

**Callers** must grant `permissions: id-token: write` (the reusable workflows deliberately declare no job
`permissions`, so they inherit the caller's and existing callers keep working). With `secrets: inherit`, optional
fallbacks work without declaration: `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TAILSCALE_AUTHKEY`,
`INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`.

Secrets live in Infisical at `<path>` per service (default `/<release_name>` for Helm, `/<docker_image>` for k8s); the
environment slug is the workflow's `environment` input.

# License

This project is released under the [MIT License](LICENSE).
