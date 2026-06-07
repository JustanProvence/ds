import os
import tempfile
import json
import pytest
from design_system import TokenManager, ThemeState


def test_token_manager_loading_and_resolution():
    # Verify TokenManager loads the tokens.json and resolves standard tokens
    manager = TokenManager()
    
    # Primitives
    assert manager.get_color("primitive.color.blue.600") == "#2563EB"
    assert manager.get_color("blue.600") == "#2563EB"
    
    # Semantics (Light Mode)
    assert manager.get_color("semantic.color.background") == "#F9FAFB"
    assert manager.get_color("background") == "#F9FAFB"
    assert manager.get_color("primary") == "#2563EB"
    
    # Components (Light Mode)
    assert manager.get_color("component.button.bg") == "#2563EB"
    assert manager.get_color("button.bg") == "#2563EB"


def test_dark_mode_overrides():
    manager = TokenManager()
    
    # In light mode (dark=False)
    assert manager.get_color("background", dark=False) == "#F9FAFB"
    assert manager.get_color("foreground", dark=False) == "#111827"
    
    # In dark mode (dark=True)
    assert manager.get_color("background", dark=True) == "#030712"
    assert manager.get_color("foreground", dark=True) == "#F9FAFB"
    
    # Unchanged in dark mode (falls back to light semantic / primitive)
    assert manager.get_color("primary", dark=True) == "#2563EB"


def test_dimension_parsing():
    # Static method
    assert TokenManager.parse_dimension("0.25rem") == 4.0
    assert TokenManager.parse_dimension("1rem") == 16.0
    assert TokenManager.parse_dimension("0.5rem") == 8.0
    assert TokenManager.parse_dimension("1.25rem") == 20.0
    assert TokenManager.parse_dimension("12px") == 12.0
    assert TokenManager.parse_dimension("9999px") == 9999.0
    assert TokenManager.parse_dimension(15) == 15.0
    assert TokenManager.parse_dimension("none") == "none"

    # Instance spacing resolution
    manager = TokenManager()
    assert manager.get_spacing("primitive.spacing.4") == 16.0
    assert manager.get_spacing("spacing.4") == 16.0
    assert manager.get_spacing("4") == 16.0
    assert manager.get_spacing("component") == 16.0

    # Instance radius resolution
    assert manager.get_radius("primitive.radius.md") == 6.0
    assert manager.get_radius("radius.md") == 6.0
    assert manager.get_radius("md") == 6.0
    assert manager.get_radius("default") == 4.0

    # Instance font size resolution
    assert manager.get_font_size("primitive.fontSize.sm") == 14.0
    assert manager.get_font_size("fontSize.sm") == 14.0
    assert manager.get_font_size("sm") == 14.0
    assert manager.get_font_size("base") == 16.0


def test_normalization():
    manager = TokenManager()
    
    # Test dashes and underscores normalization
    assert manager.get_color("button-bg") == "#2563EB"
    assert manager.get_color("button_bg") == "#2563EB"
    
    assert manager.get_color("primary-hover") == "#1D4ED8"
    assert manager.get_color("primary_hover") == "#1D4ED8"


def test_theme_priority():
    manager = TokenManager()
    
    # In tokens.json, component.button.radius is "{primitive.radius.md}" (6px)
    # whereas general "md" radius is also 6px, and "default" spacing is 4px.
    # Let's verify that lookup by specific key returns the highest priority (Component > Semantic > Primitive)
    # "background" exists in both primitive (under color.background? No, gray.50) and semantic.
    # We want to make sure semantic.color.background takes priority over any shorthand of primitive.
    assert manager.get_color("background") == "#F9FAFB"


def test_key_errors():
    manager = TokenManager()
    
    with pytest.raises(KeyError):
        manager.get_color("non_existent_token")
        
    with pytest.raises(KeyError):
        manager.get_spacing("non_existent_spacing")


def test_circular_reference_detection():
    # Create a temporary tokens file with a circular reference
    bad_tokens = {
        "primitive": {
            "color": {
                "a": { "$value": "{primitive.color.b}", "$type": "color" },
                "b": { "$value": "{primitive.color.a}", "$type": "color" }
            }
        }
    }
    
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(bad_tokens, f)
        temp_path = f.name
        
    try:
        with pytest.raises(ValueError, match="Circular reference detected"):
            TokenManager(filepath=temp_path)
    finally:
        os.remove(temp_path)


def test_theme_state_reactivity():
    tokens = TokenManager()
    theme = ThemeState(tokens=tokens)
    
    # Default light
    assert theme.dark is False
    assert theme.get_color("background") == "#F9FAFB"
    
    # Toggle to dark
    theme.toggle()
    assert theme.dark is True
    assert theme.get_color("background") == "#030712"
    
    # Toggle back
    theme.toggle()
    assert theme.dark is False
    assert theme.get_color("background") == "#F9FAFB"


def test_theme_provider():
    import flet as ft
    from design_system import ThemeProvider, ThemeState
    
    theme = ThemeState()
    # Inside a unit test environment, calling ThemeProvider directly will raise a RuntimeError
    # because Flet expects an active renderer. But catching this shows that the call reaches Flet's internals successfully.
    with pytest.raises(RuntimeError, match="No current renderer is set"):
        ThemeProvider(theme, ft.Text("hello"))
        
    with pytest.raises(RuntimeError, match="No current renderer is set"):
        ThemeProvider(theme, lambda: ft.Text("hello"))
