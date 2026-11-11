import threading
import time
import desktop_server
from playwright.sync_api import sync_playwright

t = threading.Thread(target=desktop_server.start_server, args=(58241,), daemon=True)
t.start()
time.sleep(0.5)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1360, 'height': 880})
    page.goto('http://127.0.0.1:58241/')
    page.wait_for_timeout(500)

    # 1. Screenshot Intro Splash
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_intro.png')

    # Skip intro
    page.click('.intro-skip-btn')
    page.wait_for_timeout(600)

    # 2. Screenshot Dashboard with Dynamic Candidate Name
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_dashboard.png')

    # 3. Click 'Find Jobs' via index or text
    nav_items = page.locator('.nav-item').all()
    for item in nav_items:
        if 'Find Jobs' in item.inner_text():
            item.click()
            break
    page.wait_for_timeout(600)
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_find_jobs.png')

    # 4. Click 'Email Applications'
    for item in nav_items:
        if 'Email Applications' in item.inner_text():
            item.click()
            break
    page.wait_for_timeout(600)
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_email_applications.png')

    # 5. Click 'CV Intelligence'
    for item in nav_items:
        if 'CV Intelligence' in item.inner_text():
            item.click()
            break
    page.wait_for_timeout(600)
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_cv_intelligence.png')

    # 6. Click 'Recruiter Contacts'
    for item in nav_items:
        if 'Recruiter Contacts' in item.inner_text():
            item.click()
            break
    page.wait_for_timeout(600)
    page.screenshot(path='C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/desktop_screen_contacts.png')

    browser.close()

print('All 6 screen captures completed successfully!')
