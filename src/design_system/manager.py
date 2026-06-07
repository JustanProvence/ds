import json
import os
from typing import Any, Dict, List, Optional, Set, Union


class TokenManager:
    """
    Manages three-layer design tokens (Primitive, Semantic, Component) 
    with O(1) resolution and recursive reference solving.
    """

    def __init__(self, filepath: Optional[str] = None):
        self._priorities: Dict[str, int] = {}
        self._cache_light: Dict[str, Any] = {}
        self._cache_dark: Dict[str, Any] = {}
        self.tokens_data: Dict[str, Any] = {}

        if filepath is None:
            # Look in repository root or standard locations
            possible_paths = [
                "tokens.json",
                os.path.join(os.getcwd(), "tokens.json"),
                os.path.join(os.path.dirname(__file__), "../../../tokens.json"),
                os.path.join(os.path.dirname(__file__), "../../tokens.json"),
                os.path.join(os.path.dirname(__file__), "tokens.json"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    filepath = os.path.abspath(path)
                    break

        if filepath is None or not os.path.exists(filepath):
            raise FileNotFoundError("Could not find tokens.json in any standard location.")

        with open(filepath, "r") as f:
            self.tokens_data = json.load(f)

        self._precompile()

    def _normalize_key(self, key: str) -> str:
        """
        Normalizes lookup keys (e.g., converts dashes and underscores to dots, lowercases).
        This allows 'button-bg', 'button_bg', and 'button.bg' to refer to the same token.
        """
        if not isinstance(key, str):
            return str(key)
        return key.replace("-", ".").replace("_", ".").lower()

    def _traverse_dict(self, d: Any, path: List[str]) -> Any:
        """Helper to navigate a nested dictionary using a list of path keys."""
        curr = d
        for part in path:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                return None
        return curr

    def _get_raw_value_by_path(self, path: List[str], dark: bool = False) -> Any:
        """
        Gets the raw token dictionary from the JSON, checking dark overrides
        before falling back to the standard definition.
        """
        # Under dark mode, check dark semantic overrides first
        if dark:
            dark_path = ["dark"] + path
            val = self._traverse_dict(self.tokens_data, dark_path)
            if val is not None:
                return val

        # Otherwise look in normal path
        return self._traverse_dict(self.tokens_data, path)

    def _resolve_path_to_value(self, path: List[str], dark: bool = False, visited: Optional[Set[Any]] = None) -> Any:
        """
        Recursively resolves references (e.g. "{primitive.color.gray.50}") to their final values.
        Detects and raises an error on circular references.
        """
        if visited is None:
            visited = set()

        path_tuple = (tuple(path), dark)
        if path_tuple in visited:
            raise ValueError(f"Circular reference detected: {'.'.join(path)}")
        visited.add(path_tuple)

        raw_token = self._get_raw_value_by_path(path, dark)
        if raw_token is None:
            return None

        # Resolve leaf node value
        if isinstance(raw_token, dict) and "$value" in raw_token:
            val = raw_token["$value"]
        else:
            return None

        # Check if the value is a reference path, e.g., "{primitive.color.blue.500}"
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            ref_path_str = val[1:-1]
            ref_path = ref_path_str.split(".")
            return self._resolve_path_to_value(ref_path, dark, visited)

        return val

    def _find_all_leaf_paths(self, d: Any, current_path: Optional[List[str]] = None) -> List[List[str]]:
        """Finds all token paths ending in a leaf node ($value)."""
        if current_path is None:
            current_path = []

        paths = []
        if isinstance(d, dict):
            if "$value" in d:
                paths.append(current_path)
            else:
                for k, v in d.items():
                    # Skip root level non-token sections
                    if len(current_path) == 0 and k in ("dark", "$schema"):
                        continue
                    paths.extend(self._find_all_leaf_paths(v, current_path + [k]))
        return paths

    def _get_shorthands_for_path(self, path: List[str]) -> List[str]:
        """Generates shorthand lookup strings for a given full path."""
        if not path:
            return []

        shorthands = []
        # Shorthand 1: Omit the category (e.g. "primitive", "semantic", "component")
        # e.g., "primitive.color.gray.50" -> "color.gray.50"
        if len(path) > 1:
            shorthands.append(".".join(path[1:]))

        # Shorthand 2: Omit the category and sub-category
        # e.g., "primitive.color.gray.50" -> "gray.50"
        # "semantic.color.background" -> "background"
        if len(path) > 2 and path[0] in ("primitive", "semantic"):
            shorthands.append(".".join(path[2:]))

        return shorthands

    def _add_to_cache_with_priority(self, cache: Dict[str, Any], key: str, value: Any, path: List[str]):
        """
        Adds a key-value pair to the cache, respecting priority of the token layer:
        Component (3) > Semantic (2) > Primitive (1)
        """
        category = path[0]
        priority_map = {"component": 3, "semantic": 2, "primitive": 1}
        priority = priority_map.get(category, 0)

        normalized_key = self._normalize_key(key)
        priority_key = f"{normalized_key}_priority"
        existing_priority = self._priorities.get(priority_key, 0)

        if normalized_key not in cache or priority >= existing_priority:
            cache[normalized_key] = value
            self._priorities[priority_key] = priority

    def _precompile(self):
        """Pre-resolves and flattens all tokens for light and dark modes to ensure O(1) lookups."""
        leaf_paths = self._find_all_leaf_paths(self.tokens_data)

        for path in leaf_paths:
            dot_path = ".".join(path)

            resolved_light = self._resolve_path_to_value(path, dark=False)
            resolved_dark = self._resolve_path_to_value(path, dark=True)

            # Add the full canonical path to caches
            self._add_to_cache_with_priority(self._cache_light, dot_path, resolved_light, path)
            self._add_to_cache_with_priority(self._cache_dark, dot_path, resolved_dark, path)

            # Generate and cache shorthands
            shorthands = self._get_shorthands_for_path(path)
            for sh in shorthands:
                self._add_to_cache_with_priority(self._cache_light, sh, resolved_light, path)
                self._add_to_cache_with_priority(self._cache_dark, sh, resolved_dark, path)

    @staticmethod
    def parse_dimension(val: Any) -> Any:
        """
        Parses CSS-like design token dimensions into Flet-compatible float/int pixel values.
        Handles rem, em, px, and raw numeric values.
        """
        if isinstance(val, (int, float)):
            return float(val)
        if not isinstance(val, str):
            return val

        val_str = val.strip()
        # Handle rem and em (assumes 1rem/em = 16px)
        if val_str.endswith("rem"):
            try:
                return float(val_str[:-3]) * 16.0
            except ValueError:
                pass
        elif val_str.endswith("em"):
            try:
                return float(val_str[:-2]) * 16.0
            except ValueError:
                pass
        elif val_str.endswith("px"):
            try:
                return float(val_str[:-2])
            except ValueError:
                pass

        try:
            return float(val_str)
        except ValueError:
            return val_str

    def get_color(self, name: str, dark: bool = False, default: Optional[str] = None) -> str:
        """Gets resolved color token value (hex string)."""
        cache = self._cache_dark if dark else self._cache_light
        normalized = self._normalize_key(name)
        if normalized in cache:
            return cache[normalized]
        if default is not None:
            return default
        raise KeyError(f"Color token '{name}' not found.")

    def get_spacing(self, name: str, default: Optional[Union[float, int, str]] = None) -> float:
        """Gets resolved spacing token value parsed into virtual pixels."""
        normalized = self._normalize_key(name)
        # Try spacing namespace prefixes first to resolve ambiguities correctly
        for prefix in ["spacing.", "primitive.spacing.", "semantic.spacing."]:
            pref_norm = self._normalize_key(prefix + name)
            if pref_norm in self._cache_light:
                return self.parse_dimension(self._cache_light[pref_norm])

        if normalized in self._cache_light:
            return self.parse_dimension(self._cache_light[normalized])
        if default is not None:
            return self.parse_dimension(default)
        raise KeyError(f"Spacing token '{name}' not found.")

    def get_radius(self, name: str, default: Optional[Union[float, int, str]] = None) -> float:
        """Gets resolved radius token value parsed into virtual pixels."""
        normalized = self._normalize_key(name)
        for prefix in ["radius.", "primitive.radius."]:
            pref_norm = self._normalize_key(prefix + name)
            if pref_norm in self._cache_light:
                return self.parse_dimension(self._cache_light[pref_norm])

        if normalized in self._cache_light:
            return self.parse_dimension(self._cache_light[normalized])
        if default is not None:
            return self.parse_dimension(default)
        raise KeyError(f"Radius token '{name}' not found.")

    def get_font_size(self, name: str, default: Optional[Union[float, int, str]] = None) -> float:
        """Gets resolved fontSize token value parsed into virtual pixels."""
        normalized = self._normalize_key(name)
        for prefix in ["fontsize.", "font_size.", "primitive.fontsize.", "primitive.font_size."]:
            pref_norm = self._normalize_key(prefix + name)
            if pref_norm in self._cache_light:
                return self.parse_dimension(self._cache_light[pref_norm])

        if normalized in self._cache_light:
            return self.parse_dimension(self._cache_light[normalized])
        if default is not None:
            return self.parse_dimension(default)
        raise KeyError(f"Font size token '{name}' not found.")
