# Flet Token-Driven Design System

A production-ready, fully token-driven **Design System** built with **Flet** and **Python**, packaged and managed using **Poetry**. 

This library translates professional design tokens (following industry-standard JSON schemas) into responsive, dynamic, and light/dark theme-swappable Flet components in $O(1)$ lookup time.

---

## 🚀 Key Features

*   **Three-Layer Token Scheme:** Grouped strictly into global *Primitives*, context-dependent *Semantics* (mapped separately for light/dark modes), and *Component*-specific overrides.
*   **Recursive Reference Solving:** Dynamic path resolution (resolves references like `"{semantic.color.primary}"` -> `"{primitive.color.blue.600}"` -> `"#2563EB"`) compiled once on startup for $O(1)$ lookups.
*   **Responsive Theme Swapping:** Built-in observable `ThemeState`, context provider `ThemeProvider`, and `use_theme()` hooks that trigger reactive UI re-renders of standard Flet controls on theme toggles.
*   **Flet API Refinements:** Custom unit parser that seamlessly translates CSS tokens (like `rem`, `em`, `px`) into Flet virtual pixels (e.g. `1rem` -> `16.0px`), respecting WSL and headless-compatibilities.
*   **Dual Testing Suite:** Covered by robust Unit Tests and automated Playwright Browser integration tests designed specifically for Flet/Flutter Web's semantics tree.

---

## 📂 Project Structure

```text
ds/
├── tokens.json                     # Central design tokens schema (single source of truth)
├── pyproject.toml                  # Poetry packaging configuration
├── poetry.lock                     # Staged Poetry dependencies lockfile
├── src/
│   └── design_system/
│       ├── __init__.py             # Public API exports (TokenManager, ThemeState, use_theme)
│       ├── manager.py              # TokenManager (reference resolution, caching, unit parsing)
│       ├── theme.py                # Reactive ThemeState, use_theme hook, and ThemeProvider
│       └── example/
│           ├── __init__.py
│           ├── main.py             # Sibling router-based example app
│           └── example.py          # Interactive, fully token-driven design system example
└── tests/
    ├── conftest.py                 # Isolated pytest background Flet server fixture
    ├── test_design_system.py       # Core TokenManager & ThemeState Unit Tests
    └── test_example_ui.py          # E2E Playwright Browser tests
```

---

## 📦 Getting Started

### Prerequisites

*   **Python:** Version `3.12+`
*   **Poetry:** For package installation and management ([Install Poetry](https://python-poetry.org/docs/#installation))

### Installation & Build

1.  **Clone the repository** and navigate to the project directory:
    ```bash
    git clone https://github.com/JustanProvence/ds.git
    cd ds
    ```

2.  **Install dependencies and build the virtual environment:**
    ```bash
    poetry install
    ```

---

## 🖥️ Running the Application

Because headless virtual machines and standard WSL environments lack native desktop window graphics libraries, the example app runs in **Web Browser Mode** on port `8550`.

Start the interactive design system example application:
```bash
poetry run python src/design_system/example/example.py
```

Open your browser and navigate to **`http://localhost:8550`**.
*   *Note:* Click the Moon/Sun icon in the navigation bar to dynamically swap between Light and Dark mode swatches and layouts!

---

## 🧪 Running the Test Suites

This project contains two distinct test suites designed to verify backend token parsing and frontend user flows.

### 1. Running Unit Tests

These tests verify the core backend token parsing, semantic overlays, priorities, normalization, and circular reference detection.

Run the unit tests:
```bash
poetry run pytest tests/test_design_system.py -v
```

---

### 2. Running Playwright UI/Browser Tests

These browser integration tests spin up the Flet server in the background, navigate headlessly using Chromium, activate the semantic overlay, and verify login/logout redirects, navigation router chains, and active theme switches.

#### **Step 1: Install Browser Engines and Dependencies**
Playwright requires browser binaries and several OS-level system libraries (like `libnspr4` and `libnss3`). Install them with:
```bash
poetry run playwright install --with-deps
```

#### **Step 2: Run Browser Integration Tests**
Execute the automated browser UI tests:
```bash
poetry run pytest tests/test_example_ui.py -s
```

---

## 🎨 Token Architecture Details

Tokens are defined inside `tokens.json` following standard schemas:

```
Primitive (raw values) ──> Semantic (purpose aliases) ──> Component (specific properties)
```

For instance, calling `theme.get_color("button.bg")` performs the following lookup behind the scenes:
1.  **Component:** `"component.button.bg"` maps to `"{semantic.color.primary}"`.
2.  **Semantic:** Checks `"dark.semantic.color.primary"` (if dark mode is active) or falls back to `"semantic.color.primary"` -> `"{primitive.color.blue.600}"`.
3.  **Primitive:** Resolves `"primitive.color.blue.600"` -> `"#2563EB"`.
