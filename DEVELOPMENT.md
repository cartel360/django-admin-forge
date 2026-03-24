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

### Artifacts

```bash
python -m build
twine check dist/*
```

Pass **file globs** to `twine check`, not the `dist` directory alone: `twine check dist/*`.

### Upload

1. Bump `version` in `pyproject.toml`.
2. Install tooling: `pip install ".[publish]"` (or `pip install build twine`).
3. `twine upload dist/*` (use API token user `__token__`).

Optional dry run on [TestPyPI](https://test.pypi.org/): `twine upload --repository testpypi dist/*`.

### Trusted publishing (GitHub Actions)

If you use PyPI **trusted publishing**, the workflow name you register on PyPI must match the workflow **file** under `.github/workflows/` (for example `publish.yml`) and the repository you authorize.

## Contributing

- Open an issue or PR with a short description of the change and any UI screenshots for visual work.
- Keep changes focused; follow patterns already present in the touched modules.
- Add or extend tests when behavior changes.

Further context: [docs/architecture.md](docs/architecture.md), [docs/roadmap.md](docs/roadmap.md).
