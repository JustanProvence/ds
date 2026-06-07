from dataclasses import dataclass
from typing import Any, Callable, Optional, Union
import flet as ft

from .manager import TokenManager


@ft.observable
@dataclass
class ThemeState:
    """
    An observable and reactive theme state holding the active light/dark mode
    and an instance of TokenManager. Standard Flet components that use this 
    state will automatically re-render when the theme mode is toggled.
    """
    dark: bool = False
    tokens: Optional[TokenManager] = None

    def __post_init__(self):
        if self.tokens is None:
            self.tokens = TokenManager()

    def toggle(self):
        """Toggles between light and dark mode."""
        self.dark = not self.dark

    def set_dark_mode(self, value: bool):
        """Sets the dark mode state explicitly."""
        self.dark = value

    def get_color(self, name: str, default: Optional[str] = None) -> str:
        """Retrieves resolved color token under the current dark/light mode state."""
        return self.tokens.get_color(name, dark=self.dark, default=default)

    def get_spacing(self, name: str, default: Any = None) -> float:
        """Retrieves resolved spacing token under the current dark/light mode state."""
        return self.tokens.get_spacing(name, default=default)

    def get_radius(self, name: str, default: Any = None) -> float:
        """Retrieves resolved radius token under the current dark/light mode state."""
        return self.tokens.get_radius(name, default=default)

    def get_font_size(self, name: str, default: Any = None) -> float:
        """Retrieves resolved font size token under the current dark/light mode state."""
        return self.tokens.get_font_size(name, default=default)


# Create Flet context for ThemeState
ThemeContext: ft.ContextProvider[Optional[ThemeState]] = ft.create_context(None)


_global_theme_state: Optional[ThemeState] = None


def use_theme() -> ThemeState:
    """
    A Flet hook to retrieve the current reactive ThemeState from the ThemeContext.
    Falls back to a global singleton ThemeState if not within a ThemeProvider.
    """
    try:
        theme = ft.use_context(ThemeContext)
        if theme is not None:
            return theme
    except Exception:
        # Fallback if use_context is called outside of component rendering cycle
        pass

    global _global_theme_state
    if _global_theme_state is None:
        _global_theme_state = ThemeState()
    return _global_theme_state


def ThemeProvider(state: ThemeState, content: Union[ft.Control, Callable[[], ft.Control]]) -> ft.Control:
    """
    A Flet context provider wrapper that provides ThemeState to all nested child components.
    """
    callback = content if callable(content) else lambda: content
    return ThemeContext(state, callback)
