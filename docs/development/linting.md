# Code Formatting & Linting Guide

This guide explains how to set up and use linters and formatters for both Python and TypeScript in your project. It also provides details on how to manage dev dependencies and ensure code consistency across your codebase.

## Python (Backend & Pipeline)

### Linting

To check for style violations and suggest fixes (using **Flake8**):

```bash
poetry run flake8 .
```

### Formatting

To auto-format code and sort imports (using **Black** and **isort**):

```bash
# Auto-format the code
poetry run black .

# Sort imports
poetry run isort .
```

## TypeScript / JavaScript (Frontend - Nuxt.js)

### Linting

To check for linting errors in TypeScript and JavaScript (using **ESLint**):

```bash
yarn eslint --ext .js,.ts,.
```

### Formatting

To auto-format code according to **Prettier** configuration:

```bash
yarn prettier --write .
```

## Editor Integration (VS Code)

We recommend configuring **VS Code** to automatically format on save and show linting issues in real-time. Add the following settings to `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "eslint.format.enable": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true
  }
}
```

## Development Dependencies

When we install linting and formatting tools such as **Flake8**, **Black**, **ESLint**, and **Prettier**, we add them as **dev dependencies**. This means they are only required for the development environment and are not needed in the production environment.

### Why Add Them as Dev Dependencies?

1. **Smaller Production Build**: Development dependencies like linters and formatters are not needed for running your application in production. By marking them as dev dependencies, you keep your production environment lean.

2. **Separation of Concerns**: Code linters and formatters are only used during development, and they don't affect the runtime behavior of the application. Keeping them separate from regular dependencies helps clarify their purpose.

### Python (Using Poetry)

In Poetry, dev dependencies are installed like this:

```bash
poetry add --dev black flake8 isort
```

This ensures that the tools are only installed in development.

### TypeScript/JavaScript (Using Yarn)

In the frontend, you add dev dependencies using the following command:

```bash
yarn add --dev eslint prettier eslint-plugin-vue eslint-config-prettier eslint-plugin-prettier
```

This keeps your production build free of unnecessary packages and focuses only on the essential libraries for development.

---

By following these steps and commands, you can ensure that your project maintains consistent, industry-standard code formatting and linting.
