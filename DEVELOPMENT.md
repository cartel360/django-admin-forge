# Developing django-admin-forge

Guide for contributors and anyone working from a git checkout.

## Prerequisites

- Python 3.11+
- Django 4.2+ (installed via the dev extras below)

## Environment

```bash
git clone <your-fork-or-repo-url>
cd django-admin-forge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the package in editable mode from `src/django_admin_forge/` so template and Python changes apply immediately.

## Run tests

From the repository root:

```bash
pytest
```

Settings module: `tests.settings` (see `pyproject.toml` `[tool.pytest.ini_options]`).

## Lint

```bash
ruff check src tests demo
```

Fix issues when reasonable; match existing style in files you touch.

## Demo project

The `demo/` Django project exercises the admin UI against sample models.

```bash
python demo/manage.py migrate
python demo/manage.py createsuperuser
python demo/manage.py runserver
```

Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

Demo settings live in `demo/config/settings.py` (`DJANGO_ADMIN_FORGE` examples).

## Repository layout

| Path | Role |
|------|------|
| `src/django_admin_forge/` | Installable package (Python, templates, static) |
| `tests/` | Pytest suite and minimal URL config |
| `demo/` | Local development project (not shipped on PyPI) |
| `docs/` | Extra markdown (architecture, configuration, roadmap) |

## Build and publish (maintainers)

### GitHub Actions → PyPI (recommended)

Releases are published automatically when you **publish a GitHub Release** (not a draft).

**One-time setup**

1. On GitHub: **Settings → Environments → New environment** named exactly `pypi`.  
   Optional: add required reviewers or deployment branches for extra safety.

2. On [pypi.org](https://pypi.org/manage/account/publishing/): add a **trusted publisher** for this package:
   - **PyPI project name:** `django-admin-forge` (must match `pyproject.toml` `[project] name`).
   - **Owner** / **Repository:** your GitHub user or org and repo slug.
   - **Workflow name:** `publish-pypi.yml` (the file under `.github/workflows/`).
   - **Environment name:** `pypi` (must match the workflow job).

**Each release**

1. Bump `version` in `pyproject.toml` and merge to your default branch.
2. Create a **tag** that matches the release (for example `v0.2.0` when `version = "0.2.0"`).
3. **GitHub → Releases → Draft a new release** (or publish from the tag), set target to that tag, then **Publish release**.  
   The workflow builds and uploads to PyPI; no API token in GitHub secrets is required.

**Or: tag + release from Actions**

1. Merge your version bump on the default branch (`pyproject.toml` must already say e.g. `version = "0.1.2"`).
2. **Actions → Create release tag → Run workflow**.
3. Enter the same version (`0.1.2` or `v0.1.2`). The workflow checks that it matches `pyproject.toml`, then creates the annotated tag `v0.1.2`, pushes it, and runs `gh release create` with auto-generated notes.  
   That **published** release triggers `publish-pypi.yml` the same way as a hand-made release.

### Manual upload (API token)

If you do not use trusted publishing:

1. Bump `version` in `pyproject.toml`.
2. `python -m build` then `twine check dist/*` (use globs: `dist/*`, not the `dist` folder path alone).
3. `twine upload dist/*` with username `__token__` and a PyPI API token.

Optional dry run on [TestPyPI](https://test.pypi.org/): `twine upload --repository testpypi dist/*`.

## Contributing

- Open an issue or PR with a short description of the change and any UI screenshots for visual work.
- Keep changes focused; follow patterns already present in the touched modules.
- Add or extend tests when behavior changes.

Further context: [docs/architecture.md](docs/architecture.md), [docs/roadmap.md](docs/roadmap.md).
