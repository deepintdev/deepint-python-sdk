# Changelog

All notable changes to this package are documented in this file.

## 2.0.0

AIR-Core API v2: the alerts are now automations (simple notices and flows). This release is breaking for code that uses alerts; code that does not use them keeps working unchanged.

### Breaking
- The alerts were removed from the AIR-Core API: every alert route of API v1 answers HTTP 410 Gone with the code `ALERTS_REMOVED`. Every SDK method that called them (`workspace.alerts.load/create/fetch/fetch_all`, `Alert.build/from_url/load/update/delete`, `Alert.instances.fetch`, `Alert.webhook.get/set/delete/rotate_secret/test`) now raises `DeepintAlertsRemovedError` without calling the API, naming the method that replaces it. The classes are kept, marked deprecated, so imports keep working; `AlertWebhook.verify_signature` still works.
- The SDK calls API v2 (`/api/v2/...`) by default. API v2 serves every operation of API v1 except the alerts, with the same tokens, permissions and errors.
- `Workspace.build()` loads the automations instead of the alerts, and `Workspace.to_dict()` has `automations` instead of `alerts`.

### Added
- Automations: `workspace.automations` (`WorkspaceAutomations`) with `list(kind=None|'notice'|'flow')`, `load()`, `fetch(automation_id=..., name=...)`, `fetch_all(kind=...)`, `create(...)`, `update(id, ...)`, `delete(id)`, `history(id, page, limit)` and `test(id)`; the `Automation` object (`build`, `from_url`, `load`, `update`, `delete`, `history`, `test`, `verify_webhook_signature`), `AutomationInfo` and `AutomationKind`. A create or update exposes how AIR-Core saved it and why (`saved_as`), the signing secret of a new webhook (`webhook_secret`, shown once) and its `warnings`. Changes that would alter the kind are refused by the API with `NOT_A_NOTICE` or `NOTICE_FIXED` (raised as `DeepintHTTPError`).
- `DeepintAlertsRemovedError` (a `DeepintHTTPError` with code `ALERTS_REMOVED` and the attributes `replacement` and `docs`), also raised when the API answers 410 `ALERTS_REMOVED`, for example to a custom endpoint call.
- `set_api_version()`, `get_api_version()` and the `AIRCORE_API_VERSION` environment variable select the API version (`v2` by default; `v1` is deprecated). The automations always use v2. Paths given to `CustomEndpointCall` are sent as written.
- `parse_url` and the `from_url` builders accept `/api/v2/` URLs.
- Offline tests for the automations, the API version and the removed alerts (`tests/test_automations.py`); CI runs the offline tests too.

### Fixed
- Errors of the API that are not retried (for example 404 or 409) were raised after waiting 10 seconds; they are raised at once.
- An error answer without `code` or `message` raised `KeyError` instead of `DeepintHTTPError`.
- `WorkspaceModels.fetch()` read the list of alerts instead of the list of models when the models were already loaded.

### Migrating

| Before (1.x) | Now (2.0) |
| --- | --- |
| `ws.alerts.fetch_all()` | `ws.automations.fetch_all(kind='notice')` or `ws.automations.list()` |
| `ws.alerts.fetch(alert_id=a_id)` | `ws.automations.fetch(automation_id=a_id)` |
| `ws.alerts.create(name, description, subscriptions, color, AlertType.update, source_id, condition)` | `ws.automations.create(name, trigger={'type': 'source_updated', 'source': source_id}, condition=...)` |
| `ws.alerts.create(..., alert_type=AlertType.stall, time_stall=seconds)` | `ws.automations.create(name, trigger={'type': 'stall', 'source': source_id, 'hours': hours})` |
| `Alert.build(org_id, ws_id, alert_id)` | `Automation.build(org_id, ws_id, automation_id=alert_id)` (a former alert keeps its id) |
| `alert.update(...)` / `alert.delete()` | `automation.update(...)` / `automation.delete()` |
| `alert.instances.fetch()` | `automation.history()` |
| `alert.webhook.set(url)` / `alert.webhook.delete()` | `automation.update(actions=[{'type': 'email', 'to': 'list'}, {'type': 'webhook', 'url': url}])` / the same without the webhook action |
| `alert.webhook.test()` | `automation.test()` |

## 1.6.0

Support for the features of AIR-Core 1.1.

### Added
- `Model.explanations`: `global_importances()` and `explain_prediction()` return the SHAP explanation of a model and of one prediction (the input may be a list or a one-row DataFrame; missing values are sent as null and dates as ISO 8601 text).
- `Model.card()` returns the model card (purpose, training data, evaluation, explainability, limitations).
- `Alert.webhook`: `get()` (with the number of latest deliveries), `set()`, `delete()`, `rotate_secret()` and `test()` manage the signed outgoing webhook of an alert, and `AlertWebhook.verify_signature()` checks the `x-signature-256` header in the receiver (the body may be bytes or text; a malformed header is reported as not valid).
- `Organization.ai_activity()` reads the audit log of the assistant, the MCP server and the explainability module.
- Offline tests for these requests (`tests/test_api_1_1.py`).

### Fixed
- Requests made without extra headers were sent without the `x-auth-token` header.
- `Organization(...)` raised a `TypeError` when it received a non-empty list of workspaces.
- The documentation builds again on Read the Docs (the configuration used the removed `python.version` key).
- The README said the default instance changed from `app.air-core.io`; it changed from `app.deepint.net`.

## 1.5.0

The Deep Intelligence platform is now called AIR-Core and is served at https://app.air-core.io.

### Changed
- The default instance is now `app.air-core.io` (previously `app.deepint.net`). It is used when no instance is given as a parameter, in an environment variable or in `~/.deepint.ini`.
- `Credentials.build(token=...)` now honours the instance configured in the environment or in `~/.deepint.ini` (before, a token given as a parameter always used the built-in default), so applications can keep pointing at their instance.
- Empty environment variables are ignored, so an empty `AIRCORE_*` variable does not hide a configured `DEEPINT_*` one.
- Documentation, docstrings, examples and package metadata refer to AIR-Core and use `app.air-core.io` / `air-core.io` links.

### Added
- `AIRCORE_TOKEN` and `AIRCORE_INSTANCE` environment variables. They take precedence over `DEEPINT_TOKEN` and `DEEPINT_INSTANCE`, which keep working.
- Offline tests for credentials loading (`tests/test_credentials.py`).

### Fixed
- `Credentials.build()` raised a `TypeError` instead of `DeepintCredentialsError` when no token was found and `~/.deepint.ini` did not exist.

### Compatibility
- The package name (`deepint`), import name, classes, functions and HTTP headers (`x-auth-token`, `x-deepint-organization`) are unchanged.
- An explicitly configured instance, including `app.deepint.net`, keeps working as before.
