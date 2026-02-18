# BagualesPOS Testing Guide

## Quick Start

### Run all tests (Docker)
```bash
make test
```

### Run specific app tests
```bash
make test-app app=cash
make test-app app=devices
```

### Run specific test file
```bash
make test-file file=cash/tests.py
```

### Run tests locally (faster for development)
```bash
make test-local
```

### Run with coverage
```bash
make test-coverage
```

## Testing Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests in Docker |
| `make test-app app=<name>` | Run tests for specific app |
| `make test-file file=<path>` | Run specific test file |
| `make test-fast` | Skip migrations (fastest) |
| `make test-coverage` | Generate coverage report |
| `make test-local` | Run tests locally (no Docker) |
| `make test-verbose` | Verbose output |

## Coverage Reports

After running `make test-coverage`, open `htmlcov/index.html` in your browser to see the detailed coverage report.

## Testing Best Practices

1. **Use factories** for creating test data
2. **Isolate tests** - each test should be independent
3. **Test edge cases** - not just happy paths
4. **Keep tests fast** - use in-memory DB (SQLite)
5. **Meaningful names** - `test_user_cannot_close_other_session`

## Settings

Tests use `/home/aos/Documentos/GitHub/BagualesPOS/BagualesPOS/settings/testing.py` which provides:
- Fast in-memory SQLite database
- MD5 password hasher (faster)
- Minimal logging
- Disabled caching

## CI/CD

For continuous integration:
```bash
make ci-test
```
