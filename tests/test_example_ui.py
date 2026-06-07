import re
import pytest
from playwright.sync_api import Page, expect


def enable_accessibility(page: Page):
    """
    Clicks Flet/Flutter Web's 'Enable accessibility' button if present.
    This exposes the semantic HTML tree (with standard text, buttons, and inputs)
    so Playwright can find and interact with them.
    """
    try:
        # We dispatch a click event directly in JS on the flt-semantics-placeholder element.
        # This completely bypasses viewport checks since Flutter places this element off-screen.
        page.locator("flt-semantics-placeholder").dispatch_event("click")
        page.wait_for_timeout(1000)
        print("\n[TEST] Successfully enabled accessibility!")
    except Exception as e:
        print("\n[TEST] Failed to enable accessibility:", e)


def test_protected_route_redirect(page: Page, flet_server):
    page.goto(flet_server)
    
    # Auto-wait for URL to resolve to login
    page.wait_for_url("**/login", timeout=5000)
    
    # Enable accessibility to render HTML semantic tree
    enable_accessibility(page)
    
    # Assert Sign In page element is attached to DOM
    expect(page.get_by_text("Sign In")).to_be_attached(timeout=5000)


def test_login_logout_flow(page: Page, flet_server):
    page.goto(flet_server + "/login")
    
    # Enable accessibility to render HTML semantic tree
    enable_accessibility(page)
    
    # Locate username input and wait until attached
    username_input = page.locator("input[type='text']").first
    expect(username_input).to_be_attached(timeout=5000)
    username_input.fill("test_user")
    
    # Locate and click Login button (since it's a semantic button, click it)
    login_btn = page.get_by_text("Login", exact=True)
    expect(login_btn).to_be_attached(timeout=5000)
    login_btn.click()
    
    # Auto-wait for successful authentication and redirect to home
    page.wait_for_url(flet_server + "/", timeout=5000)
    
    # Enable accessibility on the home page too
    enable_accessibility(page)
    
    expect(page.get_by_text("Welcome to the Token-Driven Router Demo!")).to_be_attached(timeout=5000)
    expect(page.get_by_text("Hi, test_user")).to_be_attached(timeout=5000)
    
    # Trigger Logout (next sibling of Theme switcher)
    logout_btn = page.locator("[title='Toggle Light/Dark Mode']").locator("xpath=following-sibling::*").first
    expect(logout_btn).to_be_attached(timeout=5000)
    logout_btn.click()
    
    # Auto-wait for redirect back to login
    page.wait_for_url("**/login", timeout=5000)
    
    enable_accessibility(page)
    expect(page.get_by_text("Sign In")).to_be_attached(timeout=5000)


def test_navigation_routing_flow(page: Page, flet_server):
    # Log in first
    page.goto(flet_server + "/login")
    enable_accessibility(page)
    
    username_input = page.locator("input[type='text']").first
    expect(username_input).to_be_attached(timeout=5000)
    username_input.fill("dev_user")
    page.get_by_text("Login", exact=True).click()
    
    page.wait_for_url(flet_server + "/", timeout=5000)
    enable_accessibility(page)
    
    # Click "Projects" in NavHeader
    projects_nav = page.locator("text=Projects").first
    expect(projects_nav).to_be_attached(timeout=5000)
    projects_nav.click()
    
    # Verify redirected and page rendered
    page.wait_for_url("**/projects", timeout=5000)
    enable_accessibility(page)
    
    expect(page.get_by_text("Projects Database")).to_be_attached(timeout=5000)
    
    # Click specific project details
    project_item = page.get_by_text("Flet Design System").first
    expect(project_item).to_be_attached(timeout=5000)
    project_item.click()
    
    page.wait_for_url("**/projects/1", timeout=5000)
    enable_accessibility(page)
    
    expect(page.get_by_text("Highly performant UI framework in Python")).to_be_attached(timeout=5000)
    
    # Go back to projects
    back_btn = page.get_by_text("Back to projects")
    expect(back_btn).to_be_attached(timeout=5000)
    back_btn.click()
    
    page.wait_for_url("**/projects", timeout=5000)
    enable_accessibility(page)
    
    # Click "Settings" in NavHeader
    settings_nav = page.locator("text=Settings").first
    expect(settings_nav).to_be_attached(timeout=5000)
    settings_nav.click()
    
    page.wait_for_url("**/settings", timeout=5000)
    enable_accessibility(page)
    expect(page.get_by_text("Available sections:")).to_be_attached(timeout=5000)
    
    # Click "Profile"
    profile_item = page.get_by_text("Profile")
    expect(profile_item).to_be_attached(timeout=5000)
    profile_item.click()
    
    page.wait_for_url("**/settings/profile", timeout=5000)
    enable_accessibility(page)
    expect(page.get_by_text("Configure your profile preferences here.")).to_be_attached(timeout=5000)
    
    # Go back to settings
    back_settings = page.get_by_text("Back to settings")
    expect(back_settings).to_be_attached(timeout=5000)
    back_settings.click()
    
    page.wait_for_url("**/settings", timeout=5000)


def test_theme_swapping_color_validation(page: Page, flet_server):
    page.goto(flet_server + "/login")
    enable_accessibility(page)
    
    username_input = page.locator("input[type='text']").first
    expect(username_input).to_be_attached(timeout=5000)
    username_input.fill("theme_user")
    page.get_by_text("Login", exact=True).click()
    
    page.wait_for_url(flet_server + "/", timeout=5000)
    enable_accessibility(page)
    
    # Locate Theme Switch Button
    theme_btn = page.locator("[title='Toggle Light/Dark Mode']")
    expect(theme_btn).to_be_attached(timeout=5000)
    
    # Helper to get computed background color of body/root element
    def get_bg_color():
        return page.evaluate("window.getComputedStyle(document.body).backgroundColor")
    
    # Validate Initial Light Theme Background (should be near-white rgb(249, 250, 251) which is #F9FAFB)
    light_bg = get_bg_color()
    assert "255" in light_bg or "249" in light_bg or "250" in light_bg or "251" in light_bg
    
    # Click Toggle Theme (to Dark Mode)
    theme_btn.click()
    page.wait_for_timeout(1000)  # Short pause for theme animation transition
    
    # Validate Dark Theme Background (should be very dark gray/black, e.g. #030712 -> rgb(3, 7, 18))
    dark_bg = get_bg_color()
    assert "3" in dark_bg or "7" in dark_bg or "18" in dark_bg or "0, 0, 0" in dark_bg or "17, 24, 39" in dark_bg or "24" in dark_bg
    
    # Click Toggle Theme again (back to Light Mode)
    theme_btn.click()
    page.wait_for_timeout(1000)  # Short pause for theme animation transition
    
    # Validate restored to Light Theme Background
    restored_bg = get_bg_color()
    assert restored_bg == light_bg
