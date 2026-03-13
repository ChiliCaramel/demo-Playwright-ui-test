# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a **Playwright Python** test automation framework for a Chinese e-commerce site (天天生鲜), built by a QA engineer migrating from Selenium. The learning goal is to understand idiomatic Playwright patterns vs Selenium habits.

**Target app**: `http://127.0.0.1:8000/` (must be running locally before tests)

## Commands

```bash
# Run all tests
pytest

# Run a single test
pytest tests/test_workflows.py::test_add_product_to_cart -v

# Run with specific environment (dev/staging/prod)
ENV=staging pytest

# Run headless (override pytest.ini default of --headed)
pytest --headless

# View Allure report (after running tests)
allure serve ./allure-results

# Open Playwright trace viewer
playwright show-trace evidence/<test_name>_trace.zip
```

## Architecture

### Page Object Model

```
BasePage (pages/base_page.py)
  └── LoginPage, HomePage, ProductDetailPage, CartPage
```

- `BasePage` provides only `goto(url)` — page objects are kept thin
- Each page class defines locators as **instance attributes in `__init__`** using Playwright's semantic locators (`get_by_role`, `get_by_text`, `get_by_placeholder`)
- Locators in Playwright are **lazy** (evaluated at action time), unlike Selenium's `find_element` which queries immediately

### Configuration

- `config/envs.yaml` — multi-environment credentials and URLs (dev/staging/prod)
- `config/settings.py` — loads the active env from `envs.yaml` via `ENV` env var; exposes `SETTINGS` dict
- `config/config.py` — Playwright trace/browser config constants (`CONFIG_TRACE`)
- `pytest.ini` — sets default `--headed --slowmo 500`, Allure output dir, and `pythonpath = .`

### Test Infrastructure (conftest.py)

Three key fixtures:
1. **`do_login`** — navigates to base URL, logs in, returns authenticated `Page` object
2. **`browser_context_args`** — configures video recording dir and viewport for all contexts
3. **`start_tracing`** — auto-use fixture that starts Playwright tracing for every test

One hook:
- **`pytest_runtest_makereport`** — on failure: saves screenshot + trace + video to `./evidence/` and attaches to Allure; on success: deletes video to save disk space

### Utilities

- `utils/logger_handler.py` — singleton `logger` instance; logs to both console (INFO) and timestamped file in `log/` (DEBUG)

## Learning Notes: Selenium vs Playwright Key Differences

This section exists to help future Claude instances assist the user's learning journey.

**Teaching protocol for this user**:
1. Explain "Selenium vs Playwright" contrast before any code change
2. Let the user make the change themselves
3. Review what they wrote and give feedback
4. Focus on one concept at a time

**Known Selenium habits to address in this codebase** (in suggested learning order):

1. **Assertions: `is_visible()` vs `expect()`** — `is_visible()` returns immediately (no waiting), while `expect(locator).to_be_visible()` auto-waits up to timeout. Current code uses `is_visible()` in `verifyLogin()`, `verifyHomePageLoad()`, etc.

2. **Locator definition timing** — Playwright locators defined in `__init__` are lazy (fine), but methods like `verifyLoginPageLoad()` should use `expect()` not `is_visible()` for reliable assertions.

3. **Waiting strategy** — Playwright actions auto-wait; no need for `time.sleep()` or explicit wait helpers. The `--slowmo 500` in pytest.ini is for human observation, not synchronization.

4. **Fixtures vs setUp/tearDown** — `do_login` fixture replaces Selenium's class-level setUp. Understanding `scope="function"` vs `scope="session"` matters for performance.

5. **Broken selector in CartPage** — `page.locator(".sub_page_name fl")` — `fl` should likely be `.fl` (a class), making it `.sub_page_name.fl` or a descendant selector `.sub_page_name .fl`.
