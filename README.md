# Cloud Automation Lab

A secure, modular automation platform powered by **GitHub Actions**. This repository provides a reusable framework for running legitimate automation tasks on GitHub-hosted virtual machines with a focus on security, maintainability, and extensibility.

---

## Overview

This project turns GitHub Actions into a flexible automation engine. Instead of writing one-off scripts in workflow files, you get a proper Python application with a modular task system, consistent logging, secure credential management, and full test coverage.

**Execution flow:**

```
GitHub Actions (manual trigger or cron)
      │
      ▼
GitHub-hosted Ubuntu runner
      │
      ▼
Application (src/main.py)
      │
      ▼
Selected automation task (src/tasks/)
      │
      ▼
Authorized API or service
```

---

## Architecture

```
cloud-automation/
│
├── .github/workflows/
│   ├── automation.yml        # Main workflow (manual + scheduled)
│   └── scheduled-tasks.yml   # Independent scheduled tasks
│
├── src/
│   ├── main.py               # Application entry point
│   ├── config.py             # Environment configuration
│   ├── logger.py             # Consistent, safe logging
│   │
│   └── tasks/
│       ├── __init__.py       # Task registry (auto-discovery)
│       ├── example_task.py   # Demonstration task
│       ├── system_info_task.py  # VM information
│       ├── public_api_task.py   # Public API example
│       ├── authed_api_template.py  # Authenticated API template
│       ├── file_processing_task.py  # File processing with artifacts
│       │
│       └── browser/          # Optional browser automation module
│           └── __init__.py
│
├── scripts/
│   └── example.sh            # Example shell script
│
├── tests/
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_tasks.py
│   └── test_main.py
│
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
└── LICENSE
```

### Key design decisions

- **Modular tasks**: Each automation is an independent, self-contained module with a single `run()` function
- **Auto-discovery**: New tasks are automatically discovered — no central registry to update
- **Safe logging**: All logs are sanitized to prevent accidental credential exposure
- **Least privilege**: Workflows request only the permissions they actually need
- **Environment-based config**: Every credential comes from environment variables (GitHub Secrets)

---

## Available Tasks

| Task Name | Description | Credentials Required |
|-----------|-------------|---------------------|
| `example` | Simple demonstration that prints a message | No |
| `system_info` | Collects non-sensitive VM information (OS, disk, memory) | No |
| `public_api` | Calls a public API with error handling and JSON parsing | No |
| `authed_api` | Template for accessing an authorized API | Yes — see Secrets |
| `file_processing` | Downloads and processes data, generates artifacts | No |

---

## Local Setup

```bash
# Clone the repository
git clone https://github.com/aura-fyll/cloud-automation-lab.git
cd cloud-automation-lab

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment template for local testing
cp .env.example .env
# Edit .env with your test values — never commit this file
```

### Running locally

```bash
# List available tasks
python src/main.py --list-tasks

# Run the example task
python src/main.py --task example

# Run the system info task
python src/main.py --task system_info

# Run with verbose logging
python src/main.py --task public_api --verbose
```

---

## GitHub Actions Setup

### Enabling Actions

The repository comes with two workflows:

1. **Automation** (`automation.yml`) — The main workflow. Can be triggered manually or runs daily at 06:00 UTC.
2. **Scheduled Tasks** (`scheduled-tasks.yml`) — Runs `system_info` and `public_api` tasks every 6 hours.

These workflows are automatically available when you push the repository. Go to your repository's **Actions** tab to see them.

### Required Secrets

For tasks that don't require credentials (example, system_info, public_api, file_processing), no secrets are needed.

For the `authed_api` template or future authenticated tasks, add these secrets:

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `SERVICE_API_TOKEN` | API token for the authorized service | `authed_api` task |
| `SERVICE_BASE_URL` | Base URL of the API (e.g., `https://api.example.com/v1`) | `authed_api` task |

To add secrets:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret name and its value

### Running a Workflow Manually

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Click **Automation** in the left sidebar
4. Click **Run workflow**
5. Select a task from the dropdown
6. Click **Run workflow**

The workflow will spin up a GitHub-hosted runner, check out the code, install dependencies, and execute your selected task.

### Scheduled Execution

The main workflow runs daily at 06:00 UTC by default. The `scheduled-tasks.yml` workflow runs every 6 hours.

To customize the schedule, edit the `cron` expression in `.github/workflows/automation.yml`:

```
on:
  schedule:
    - cron: "0 6 * * *"   # Daily at 06:00 UTC
```

---

## Adding a New Task

Adding a new automation is deliberately simple:

### 1. Create a new file in `src/tasks/`

```python
# src/tasks/my_new_task.py

from src.tasks import register_task
from src.logger import get_logger

logger = get_logger(__name__)


@register_task(
    name="my_new_task",
    description="What my task does"
)
def run():
    """Run my new automation task."""
    logger.info("My new task started.")

    # Your automation logic goes here
    result = do_something()

    logger.info("My new task completed successfully.")
    return {"status": "success", "result": result}
```

### 2. Add the task to the workflow dropdown

Edit `.github/workflows/automation.yml` and add your task name to the `options` list:

```yaml
workflow_dispatch:
  inputs:
    task:
      type: choice
      options:
        - example
        - system_info
        # ... add your task here
        - my_new_task
```

### 3. If your task needs secrets

Add them to the `Run automation task` step's `env` section in the workflow:

```yaml
- name: Run automation task
  env:
    MY_API_KEY: ${{ secrets.MY_API_KEY }}
  run: |
    python src/main.py --task "${{ env.TASK_NAME }}"
```

That's it. The task is automatically discovered by the registry and ready to run.

---

## Security

### Credential Management

- **All credentials** come from GitHub Secrets (environment variables)
- **Never hardcode** passwords, tokens, API keys, or any sensitive value
- The `.env.example` file contains **placeholders only** — never real values
- `.env` files are in `.gitignore` and cannot be accidentally committed

### Authentication Priority

When accessing an authorized service, authentication methods are preferred in this order:

1. Official API
2. OAuth
3. Service-specific access token
4. Application password
5. Other officially supported automation credentials

**Browser automation** should only be used when no suitable API exists and the account owner explicitly authorizes it. Never attempt to bypass CAPTCHA, MFA, rate limits, anti-bot protections, or account restrictions.

### Safe Logging

The logging system automatically redacts messages containing sensitive field names like `password`, `token`, `api_key`, `secret`, `auth`, `authorization`, `cookie`, `session`, and others.

### Least Privilege

Workflows start with read-only permissions (`contents: read`). Additional permissions are granted only when a specific task requires them, and the reason is documented.

### Third-Party Actions

Only trusted, official GitHub Actions are used:
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/upload-artifact@v4`

No community actions are used unless explicitly reviewed and pinned.

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src -v
```

Tests cover:
- Configuration validation
- Safe logging (credential redaction)
- Task registration and discovery
- Task selection from command-line arguments
- Error handling and graceful failure

Tests never require real credentials. Mocks are used for all external services.

---

## Extending the Platform

The platform is designed for extensibility. Future tasks could include:

- API monitoring and health checks
- Data processing and report generation
- Repository maintenance (labeling, cleanup)
- Notifications and alerts
- Authorized account integrations
- Website availability monitoring
- Scheduled data exports
- File format conversion
- Automated testing and CI validations

Each new task follows the same pattern: create a module, register it, add it to the workflow dropdown.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Limitations

- GitHub Actions runners have a **6-hour execution limit** per job
- Runners provide **temporary, ephemeral environments** — state does not persist between runs
- Free-tier GitHub accounts have monthly **action minutes quotas**
- The `authed_api` template requires properly configured GitHub Secrets to function
- Tasks that need browser automation require additional dependencies (`playwright` or `selenium`)