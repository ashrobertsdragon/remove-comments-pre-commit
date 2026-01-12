# Remove Comments Hook

A [pre-commit](https://pre-commit.com) hook that automatically strips inline comments from code files while preserving docstrings and strings.

## Supported Languages

- **Python** (`.py`): Uses Python's `tokenize` module to safely remove `#` comments. Preserves shebangs and coding declarations.
- **C-Style** (`.c`, `.cpp`, `.java`, `.js`, `.ts`, `.go`, `.rs`, `.php`, etc.): Removes `//` comments. Preserves `/* ... */` block comments and docstrings like `///`, `//!`, `/**`.
- **Hash-Style** (`.sh`, `.yaml`, `.yml`, `.rb`, `.pl`): Removes `#` comments.

## Usage

Add this to your `.pre-commit-config.yaml`:

```yaml
-   repo: https://github.com/ashrobertsdragon/remove-comments
    rev: v0.1.0  # Use the latest tag
    hooks:
    -   id: remove-comments
```

## Features

- **Safe Removal**: Respects strings and docstrings.
- **Multi-Language**: Automatically detects file type.
- **Preserves Formatting**: Attempts to keep vertical spacing (empty lines) where comments were removed.
