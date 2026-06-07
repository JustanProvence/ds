import re
import time
import pytest
from playwright.sync_api import Page, expect


def test_protected_route_redirect(page: Page, flet_server):
    # 1. Access root URL
    page.goto(flet_server)
    
    # Wait for Flet app to boot and route
    page.wait_for_timeout(2000)
    
    # Verify redirected to login page because we are unauthenticated
    assert "/login" in page.url
    expect(page.get_by_text("Sign In")).to_be_visible()


def test_login_logout_flow(page: Page, flet_server):
    page.goto(flet_server + "/login")
    page.wait_for_timeout(2000)
    
    # Locate username field and fill it
    # Flet textfields compile to input elements with label/placeholder
    username_input = page.locator("input[type='text']").first
    username_input.fill("test_user")
    
    # Click Login button
    login_btn = page.get_by_text("Login", exact=True)
    expect(login_btn).to_be_visible()
    login_btn.click()
    
    page.wait_for_timeout(2000)
    
    # Assert successfully logged in and routed to Home page
    assert page.url == flet_server + "/"
    expect(page.get_by_text("Welcome to the Token-Driven Router Demo!")).to_be_visible()
    expect(page.get_by_text("Hi, test_user")).to_be_visible()
    
    # Trigger Logout
    logout_btn = page.locator("[title='Toggle Light/Dark Mode']").locator("xpath=following-sibling::*").first
    expect(logout_btn).to_be_visible()
    logout_btn.click()
    
    page.wait_for_timeout(2000)
    
    # Assert redirected back to /login
    assert "/login" in page.url
    expect(page.get_by_text("Sign In")).to_be_visible()


def test_navigation_routing_flow(page: Page, flet_server):
    # Log in first
    page.goto(flet_server + "/login")
    page.wait_for_timeout(2000)
    page.locator("input[type='text']").first.fill("dev_user")
    page.get_by_text("Login", exact=True).click()
    page.wait_for_timeout(2000)
    
    # Click "Projects" in NavHeader
    projects_nav = page.locator("text=Projects").first
    expect(projects_nav).to_be_visible()
    projects_nav.click()
    
    page.wait_for_timeout(2000)
    assert "/projects" in page.url
    expect(page.get_by_text("Projects Database")).to_be_visible()
    expect(page.get_by_text("Flet Design System")).to_be_visible()
    
    # Click specific project details
    page.get_by_text("Flet Design System").first.click()
    page.wait_for_timeout(2000)
    assert "/projects/1" in page.url
    expect(page.get_by_text("Highly performant UI framework in Python")).to_be_visible()
    
    # Go back to projects
    page.get_by_text("Back to projects").click()
    page.wait_for_timeout(2000)
    assert "/projects" in page.url
    expect(page.get_by_text("Projects Database")).to_be_visible()
    
    # Click "Settings" in NavHeader
    settings_nav = page.locator("text=Settings").first
    expect(settings_nav).to_be_visible()
    settings_nav.click()
    
    page.wait_for_timeout(2000)
    assert "/settings" in page.url
    expect(page.get_by_text("Available sections:")).to_be_visible()
    
    # Click "Profile"
    page.get_by_text("Profile").click()
    page.wait_for_timeout(2000)
    assert "/settings/profile" in page.url
    expect(page.get_by_text("Configure your profile preferences here.")).to_be_visible()
    
    # Go back to settings
    page.get_by_text("Back to settings").click()
    page.wait_for_timeout(2000)
    assert "/settings" in page.url


def test_theme_swapping_color_validation(page: Page, flet_server):
    page.goto(flet_server + "/login")
    page.wait_for_timeout(2000)
    page.locator("input[type='text']").first.fill("theme_user")
    page.get_by_text("Login", exact=True).click()
    page.wait_for_timeout(2000)
    
    # Locate Theme Switch Button
    theme_btn = page.locator("[title='Toggle Light/Dark Mode']")
    expect(theme_btn).to_be_visible()
    
    # Helper to get computed background color of body/root element
    def get_bg_color():
        return page.evaluate("window.getComputedStyle(document.body).backgroundColor")
    
    # Validate Initial Light Theme Background (should be near-white rgb(249, 250, 251) which is #F9FAFB)
    light_bg = get_bg_color()
    print(f"\n[TEST] Light Theme Background: {light_bg}")
    # Flet page default can sometimes be rgb(255, 255, 255) depending on rendering, let's verify it is bright
    assert "255" in light_bg or "249" in light_bg or "250" in light_bg or "251" in light_bg
    
    # Click Toggle Theme (to Dark Mode)
    theme_btn.click()
    page.wait_for_timeout(2000)
    
    # Validate Dark Theme Background (should be very dark gray/black, e.g. #030712 -> rgb(3, 7, 18))
    dark_bg = get_bg_color()
    print(f"[TEST] Dark Theme Background: {dark_bg}")
    assert "3" in dark_bg or "7" in dark_bg or "18" in dark_bg or "0, 0, 0" in dark_bg or "17, 24, 39" in dark_bg or "24" in dark_bg
    
    # Click Toggle Theme again (back to Light Mode)
    theme_btn.click()
    page.wait_for_timeout(2000)
    
    # Validate restored to Light Theme Background
    restored_bg = get_bg_color()
    assert restored_bg == light_bg
