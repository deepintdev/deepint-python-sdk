# Changelog

All notable changes to this package are documented in this file.

## 1.5.0

The Deep Intelligence platform is now called AIR-Core and is served at https://app.air-core.io.

### Changed
- The default instance is now `app.air-core.io` (previously `app.deepint.net`). It is used when no instance is given as a parameter, in an environment variable or in `~/.deepint.ini`.
- Documentation, docstrings, examples and package metadata refer to AIR-Core and use `app.air-core.io` / `air-core.io` links.

### Added
- `AIRCORE_TOKEN` and `AIRCORE_INSTANCE` environment variables. They take precedence over `DEEPINT_TOKEN` and `DEEPINT_INSTANCE`, which keep working.
- Offline tests for credentials loading (`tests/test_credentials.py`).

### Fixed
- `Credentials.build()` raised a `TypeError` instead of `DeepintCredentialsError` when no token was found and `~/.deepint.ini` did not exist.

### Compatibility
- The package name (`deepint`), import name, classes, functions and HTTP headers (`x-auth-token`, `x-deepint-organization`) are unchanged.
- An explicitly configured instance, including `app.deepint.net`, keeps working as before.
