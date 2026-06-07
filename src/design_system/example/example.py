"""Token-Driven Flet Router Example with dynamic dark/light mode swapping."""

from dataclasses import dataclass
import flet as ft

from design_system import ThemeState, ThemeProvider, use_theme

# ---------------------------------------------------------------------------
# Auth context
# ---------------------------------------------------------------------------


@ft.observable
@dataclass
class AuthState:
    is_authenticated: bool = False
    username: str = ""
    is_admin: bool = False

    def login(self, username, admin=False):
        self.username = username
        self.is_authenticated = True
        self.is_admin = admin

    def logout(self):
        self.username = ""
        self.is_authenticated = False
        self.is_admin = False


AuthContext: ft.ContextProvider[AuthState | None] = ft.create_context(None)


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------


def home_loader(params):
    return {"greeting": "Welcome to the Token-Driven Router Demo!", "featured_count": 3}


def projects_loader(params):
    return [
        {"id": 1, "name": "Flet Design System", "status": "Active"},
        {"id": 2, "name": "Dynamic Token Manager", "status": "Active"},
        {"id": 3, "name": "Declarative Theme Swapping", "status": "Active"},
    ]


def project_detail_loader(params):
    projects = {
        "1": {"id": 1, "name": "Flet Design System", "description": "Highly performant UI framework in Python"},
        "2": {"id": 2, "name": "Dynamic Token Manager", "description": "O(1) reference-resolving design tokens"},
        "3": {"id": 3, "name": "Declarative Theme Swapping", "description": "Reactive light and dark mode toggles"},
    }
    return projects.get(params.get("projectId"), {"name": "Unknown", "description": ""})


def settings_loader(params):
    return {"sections": ["Profile", "Security", "Notifications"]}


# ---------------------------------------------------------------------------
# Auth components
# ---------------------------------------------------------------------------


@ft.component
def LoginPage():
    auth = ft.use_context(AuthContext)
    theme = use_theme()
    username_ref = ft.use_ref(None)

    def handle_login():
        auth.login(username_ref.current.value or "user")
        ft.context.page.navigate("/")

    def handle_admin_login():
        auth.login(username_ref.current.value or "admin", admin=True)
        ft.context.page.navigate("/")

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Sign In",
                    size=theme.get_font_size("3xl"),
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("foreground"),
                ),
                ft.TextField(
                    label="Username",
                    value="admin",
                    ref=username_ref,
                    bgcolor=theme.get_color("input.bg"),
                    border_color=theme.get_color("input.border"),
                    border_radius=theme.get_radius("input.radius"),
                    color=theme.get_color("foreground"),
                    focused_border_color=theme.get_color("input.focus-ring"),
                ),
                ft.Row(
                    [
                        ft.Button(
                            "Login",
                            on_click=lambda _: handle_login(),
                            bgcolor=theme.get_color("button.bg"),
                            color=theme.get_color("button.fg"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=theme.get_radius("button.radius")),
                            ),
                        ),
                        ft.Button(
                            "Login as Admin",
                            on_click=lambda _: handle_admin_login(),
                            bgcolor=theme.get_color("secondary"),
                            color=theme.get_color("secondary-foreground"),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=theme.get_radius("button.radius")),
                            ),
                        ),
                    ],
                    spacing=theme.get_spacing("3"),
                ),
            ],
            width=300,
            spacing=theme.get_spacing("4"),
        ),
        bgcolor=theme.get_color("background"),
        expand=True,
        padding=theme.get_spacing("8"),
        alignment=ft.alignment.Alignment.CENTER,
    )


@ft.component
def ProtectedRoute():
    auth = ft.use_context(AuthContext)
    outlet = ft.use_route_outlet()

    if auth is None:
        return ft.ProgressRing()

    if not auth.is_authenticated:
        ft.context.page.navigate("/login")
        return ft.ProgressRing()

    return outlet


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


@ft.component
def NavLink(label, path):
    active = ft.is_route_active(path)
    theme = use_theme()
    return ft.Container(
        content=ft.Text(
            label,
            weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
            color=theme.get_color("primary") if active else theme.get_color("foreground"),
            size=theme.get_font_size("sm"),
        ),
        bgcolor=theme.get_color("secondary") if active else None,
        padding=ft.Padding.symmetric(
            horizontal=theme.get_spacing("4"),
            vertical=theme.get_spacing("2"),
        ),
        border_radius=theme.get_radius("md"),
        on_click=lambda: ft.context.page.navigate(path),
    )


@ft.component
def AppLayout():
    auth = ft.use_context(AuthContext)
    theme = use_theme()
    outlet = ft.use_route_outlet()

    if auth is None:
        return ft.ProgressRing()

    return ft.Container(
        bgcolor=theme.get_color("background"),
        expand=True,
        content=ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "Design System Demo",
                                size=theme.get_font_size("lg"),
                                weight=ft.FontWeight.BOLD,
                                color=theme.get_color("foreground"),
                            ),
                            NavLink("Home", "/"),
                            NavLink("Projects", "/projects"),
                            NavLink("Settings", "/settings"),
                            ft.Text(
                                f"Hi, {auth.username}",
                                color=theme.get_color("muted-foreground"),
                                size=theme.get_font_size("sm"),
                            ),
                            # Dynamic Theme Switcher
                            ft.IconButton(
                                icon=ft.Icons.LIGHT_MODE if theme.dark else ft.Icons.DARK_MODE,
                                icon_color=theme.get_color("primary"),
                                tooltip="Toggle Light/Dark Mode",
                                on_click=lambda _: theme.toggle(),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                icon_color=theme.get_color("foreground"),
                                on_click=lambda _: (
                                    auth.logout(),
                                    ft.context.page.navigate("/login"),
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=theme.get_spacing("4"),
                    bgcolor=theme.get_color("secondary"),
                    border_radius=theme.get_radius("md"),
                ),
                ft.Divider(height=1, color=theme.get_color("border")),
                # Content area
                ft.Container(
                    content=outlet,
                    padding=theme.get_spacing("component"),
                    bgcolor=theme.get_color("background"),
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


# ---------------------------------------------------------------------------
# Page components
# ---------------------------------------------------------------------------


@ft.component
def Home():
    data = ft.use_route_loader_data()
    theme = use_theme()
    return ft.Container(
        bgcolor=theme.get_color("card.bg"),
        border_radius=theme.get_radius("card.radius"),
        border=ft.Border.all(1, theme.get_color("card.border")),
        padding=theme.get_spacing("card.padding"),
        content=ft.Column(
            [
                ft.Text(
                    data["greeting"],
                    size=theme.get_font_size("3xl"),
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("foreground"),
                ),
                ft.Text(
                    f"{data['featured_count']} featured projects available",
                    size=theme.get_font_size("base"),
                    color=theme.get_color("muted-foreground"),
                ),
                ft.Button(
                    "Browse projects",
                    bgcolor=theme.get_color("button.bg"),
                    color=theme.get_color("button.fg"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=theme.get_radius("button.radius")),
                    ),
                    on_click=lambda _: ft.context.page.navigate("/projects"),
                ),
            ],
            spacing=theme.get_spacing("4"),
        ),
    )


@ft.component
def ProjectsList():
    data = ft.use_route_loader_data()
    theme = use_theme()
    return ft.Column(
        [
            ft.Text(
                "Projects Database",
                size=theme.get_font_size("2xl"),
                weight=ft.FontWeight.BOLD,
                color=theme.get_color("foreground"),
            ),
            *[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text(
                                        p["name"],
                                        size=theme.get_font_size("lg"),
                                        weight=ft.FontWeight.BOLD,
                                        color=theme.get_color("foreground"),
                                    ),
                                    ft.Text(
                                        p["status"],
                                        size=theme.get_font_size("sm"),
                                        color=theme.get_color("muted-foreground"),
                                    ),
                                ]
                            ),
                            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14, color=theme.get_color("muted-foreground")),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=theme.get_color("card.bg"),
                    border_radius=theme.get_radius("md"),
                    border=ft.Border.all(1, theme.get_color("border")),
                    padding=theme.get_spacing("4"),
                    on_click=lambda _, pid=p["id"]: ft.context.page.navigate(f"/projects/{pid}"),
                )
                for p in data
            ],
        ],
        spacing=theme.get_spacing("3"),
    )


@ft.component
def ProjectDetails():
    data = ft.use_route_loader_data()
    params = ft.use_route_params()
    location = ft.use_route_location()
    theme = use_theme()

    return ft.Container(
        bgcolor=theme.get_color("card.bg"),
        border_radius=theme.get_radius("card.radius"),
        border=ft.Border.all(1, theme.get_color("card.border")),
        padding=theme.get_spacing("card.padding"),
        content=ft.Column(
            [
                ft.Text(
                    data["name"],
                    size=theme.get_font_size("2xl"),
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("foreground"),
                ),
                ft.Text(data["description"], size=theme.get_font_size("base"), color=theme.get_color("foreground")),
                ft.Divider(color=theme.get_color("border")),
                ft.Text(
                    f"Project ID: {params['projectId']}",
                    italic=True,
                    size=theme.get_font_size("sm"),
                    color=theme.get_color("muted-foreground"),
                ),
                ft.Text(
                    f"Location: {location}",
                    italic=True,
                    size=theme.get_font_size("xs"),
                    color=theme.get_color("muted-foreground"),
                ),
                ft.Button(
                    "Back to projects",
                    bgcolor=theme.get_color("button.bg"),
                    color=theme.get_color("button.fg"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=theme.get_radius("button.radius")),
                    ),
                    on_click=lambda _: ft.context.page.navigate("/projects"),
                ),
            ],
            spacing=theme.get_spacing("4"),
        ),
    )


@ft.component
def ProjectsLayout():
    outlet = ft.use_route_outlet()
    theme = use_theme()
    return ft.Column(
        [
            ft.Container(
                content=ft.Text(
                    "PROJECTS TRACKER",
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("primary-foreground"),
                    size=theme.get_font_size("xs"),
                ),
                bgcolor=theme.get_color("primary"),
                padding=ft.Padding.symmetric(
                    horizontal=theme.get_spacing("3"),
                    vertical=theme.get_spacing("1"),
                ),
                border_radius=theme.get_radius("sm"),
            ),
            outlet,
        ],
        spacing=theme.get_spacing("4"),
    )


@ft.component
def SettingsHome():
    data = ft.use_route_loader_data()
    theme = use_theme()
    return ft.Column(
        [
            ft.Text(
                "Settings",
                size=theme.get_font_size("2xl"),
                weight=ft.FontWeight.BOLD,
                color=theme.get_color("foreground"),
            ),
            ft.Text(
                "Available sections:",
                size=theme.get_font_size("base"),
                color=theme.get_color("muted-foreground"),
            ),
            *[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                section,
                                size=theme.get_font_size("base"),
                                weight=ft.FontWeight.BOLD,
                                color=theme.get_color("foreground"),
                            ),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=theme.get_color("muted-foreground")),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=theme.get_color("card.bg"),
                    border_radius=theme.get_radius("md"),
                    border=ft.Border.all(1, theme.get_color("border")),
                    padding=theme.get_spacing("4"),
                    on_click=lambda _, s=section: ft.context.page.navigate(f"/settings/{s.lower()}"),
                )
                for section in data["sections"]
            ],
        ],
        spacing=theme.get_spacing("3"),
    )


@ft.component
def SettingsSection():
    params = ft.use_route_params()
    theme = use_theme()
    return ft.Container(
        bgcolor=theme.get_color("card.bg"),
        border_radius=theme.get_radius("card.radius"),
        border=ft.Border.all(1, theme.get_color("card.border")),
        padding=theme.get_spacing("card.padding"),
        content=ft.Column(
            [
                ft.Text(
                    f"{params['section'].title()} Settings",
                    size=theme.get_font_size("2xl"),
                    weight=ft.FontWeight.BOLD,
                    color=theme.get_color("foreground"),
                ),
                ft.Text(
                    f"Configure your {params['section']} preferences here.",
                    size=theme.get_font_size("base"),
                    color=theme.get_color("foreground"),
                ),
                ft.Button(
                    "Back to settings",
                    bgcolor=theme.get_color("button.bg"),
                    color=theme.get_color("button.fg"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=theme.get_radius("button.radius")),
                    ),
                    on_click=lambda _: ft.context.page.navigate("/settings"),
                ),
            ],
            spacing=theme.get_spacing("4"),
        ),
    )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


@ft.component
def App():
    auth, _ = ft.use_state(AuthState)
    theme, _ = ft.use_state(ThemeState)

    # Dynamically update the root page background and theme mode
    page = ft.context.page
    if page is not None:
        page.theme_mode = ft.ThemeMode.DARK if theme.dark else ft.ThemeMode.LIGHT
        page.bgcolor = theme.get_color("background")

    return ft.SafeArea(
        content=ThemeProvider(
            theme,
            content=lambda: AuthContext(
                auth,
                lambda: ft.Router(
                    [
                        ft.Route(path="login", component=LoginPage),
                        ft.Route(
                            component=ProtectedRoute,
                            children=[
                                ft.Route(
                                    component=AppLayout,
                                    children=[
                                        ft.Route(
                                            index=True,
                                            component=Home,
                                            loader=home_loader,
                                        ),
                                        ft.Route(
                                            path="projects",
                                            component=ProjectsLayout,
                                            children=[
                                                ft.Route(
                                                    index=True,
                                                    component=ProjectsList,
                                                    loader=projects_loader,
                                                ),
                                                ft.Route(
                                                    path=":projectId",
                                                    component=ProjectDetails,
                                                    loader=project_detail_loader,
                                                ),
                                            ],
                                        ),
                                        ft.Route(
                                            path="settings",
                                            children=[
                                                ft.Route(
                                                    index=True,
                                                    component=SettingsHome,
                                                    loader=settings_loader,
                                                ),
                                                ft.Route(
                                                    path=":section",
                                                    component=SettingsSection,
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ]
                ),
            ),
        )
    )


def main(page: ft.Page):
    page.title = "Flet Token-Driven Design System Demo"
    page.render(App)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("FLET_PORT", 8550))
    # In headless test environments (WSL/CI), run without launching browser window
    view = None if "FLET_PORT" in os.environ else ft.AppView.WEB_BROWSER
    ft.app(target=main, view=view, port=port)
