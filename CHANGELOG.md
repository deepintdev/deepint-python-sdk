# Changelog

All notable changes to this package are documented in this file.

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
