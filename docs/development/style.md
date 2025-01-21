# Naming Conventions

This document outlines the naming conventions to follow for different file types, folder structures, variables, and functions across Python (PEP8), Nuxt/Vue, and Shell scripts.

## General Principles
- **Consistency**: Follow the same pattern throughout the project.
- **Readability**: Names should be descriptive and easy to understand.
- **Avoid Abbreviations**: Use full words unless the abbreviation is standard and widely recognized.

---

## Filenames

| Context     | Convention       | Example             |
|-------------|------------------|---------------------|
| Python      | `snake_case.py`  | `data_processor.py` |
| Nuxt/Vue    | `kebab-case.vue` | `user-profile.vue`  |
| Shell (.sh) | `kebab-case.sh`  | `backup-script.sh`  |

- Filenames should describe the purpose or functionality.
- Avoid special characters or spaces.

---

## Folder Names

| Context  | Convention   | Example           |
|----------|--------------|-------------------|
| Python   | `snake_case` | `data_models`     |
| Nuxt/Vue | `kebab-case` | `user-management` |
| Shell    | `kebab-case` | `scripts-backup`  |

- Folder names should be plural where applicable, e.g., `components` instead of `component`.

---

## Variables

### Python (PEP8)
- Use `snake_case` for variables.
- Constants are in `UPPER_SNAKE_CASE`.

```python
user_name = "John Doe"
PI = 3.14159
```

### Nuxt/Vue
- Use `camelCase` for variables in JavaScript/TypeScript.

```javascript
let userName = "John Doe";
const maxItems = 50;
```

### Shell
- Use `UPPER_SNAKE_CASE` for environment variables and configuration.
- Use `snake_case` for local variables.

```bash
USER_NAME="John Doe"
max_items=50
```

---

## Functions

### Python (PEP8)
- Use `snake_case` for function names.
- Keep function names descriptive.

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
```

### Nuxt/Vue
- Use `camelCase` for function names in JavaScript/TypeScript.
- For Vue methods, follow the same convention.

```javascript
function calculateAverage(numbers) {
    return numbers.reduce((a, b) => a + b, 0) / numbers.length;
}

methods: {
    handleButtonClick() {
        console.log("Button clicked");
    }
}
```

### Shell
- Use `snake_case` for function names.
- Keep function names simple and descriptive.

```bash
calculate_average() {
    local sum=0
    local count=$#
    for number in "$@"; do
        sum=$((sum + number))
    done
    echo $((sum / count))
}
```

---

## Additional Notes
- **Avoid Reserved Words**: Do not use keywords or reserved words in any language as names.
- **Short and Descriptive**: Strike a balance between brevity and clarity.
- **Internationalization (i18n)**: For Nuxt/Vue, use standard prefixes for i18n files (e.g., `en.json`, `fr.json`).

---

## References
- [PEP8 - Python Naming Conventions](https://peps.python.org/pep-0008/)
- [Nuxt.js Style Guide](https://nuxt.com/docs/guide)
- [Shell Style Guide](https://google.github.io/styleguide/shellguide.html)

---
