
# ds

The first thing to do upon reading this file is to check for any global skills.

## Project Overview
A production-ready, fully token-driven **Design System** built with **Flet** and **Python**, packaged using **Poetry**. It features a central JSON token schema, light/dark mode semantic mapping, dynamic component theme-swapping, and a complete interactive documentation web application.

### Three-Layer Token Scheme (`tokens.json` & `manager.py`)
Following industry standards, design tokens are grouped into:
*   **Primitives (Global)**: Raw color hex codes, layout spacing in pixels, border radius, and typography scales.
*   **Semantic**: Purpose-oriented tags (e.g., `primary`, `background`, `surface`, `text-primary`) mapped separately for `light` and `dark` mode blocks inside `tokens.json`.
*   **Component**: Component-specific definitions referencing semantic scales.

The `TokenManager` loads this JSON and exposes simple helper methods (`get_color(name, dark=False)`, `get_spacing(name)`, `get_radius(name)`, `get_font_size(name)`) resolving all active tokens in O(1) time.

## Key software design rules

1. Applications using this are expected to use the flet.Router, therefore it is NOT a single page application. 
    1. Example: https://flet.dev/docs/cookbook/navigation-and-routing/
    1. Example: https://flet.dev/docs/cookbook/router
2. The developer should be able to use any Flet control/component without having to wrap the component in order to use the token management system developed as a part of this project.
3. Assume all flet components developed will use the Flet declarative @flet.component annotation https://flet.dev/blog/introducing-declarative-ui-in-flet/

## Key project development notes for this repository

### 1. WSL & Headless Compatibility
Because of missing media and desktop graphics libraries inside headless environments (like standard WSL or Docker VMs), Flet is configured to compile and execute in **Web Browser Mode** rather than a native desktop window:
```python
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
```
This serves a highly performant, lightweight local web application on **`http://localhost:8550`**.

### 2. Flet API Refinements and Bug-Fixes
*   **No Container Cursors**: In Flet 0.85.2, `ft.Container` does not support constructor parameters like `cursor` or `mouse_cursor`. Doing so triggers a runtime `TypeError`. Since Flet automatically displays a pointer hand when an `on_click` event is bound to a container, all hardcoded cursor definitions were removed.
*   **No Direct Text Letter-Spacing**: `letter_spacing` cannot be passed directly into the `ft.Text` initializer in this version. This parameter was removed to maintain native, robust cross-platform text layout.
