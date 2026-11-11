from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto("http://localhost:3000", wait_until="networkidle")
        
        # Scroll to contact form
        page.evaluate("window.scrollTo(0, 4800)")
        page.wait_for_timeout(500)
        
        # Fill form fields
        page.fill("input[placeholder='e.g. Alex Henderson']", "Muhammad Mubashar QA")
        page.fill("input[placeholder='alex@company.com']", "pashadev804@gmail.com")
        page.fill("textarea[placeholder='Tell us about your team, use case, or questions...']", "This is an end-to-end verified test inquiry for Pasha Hunt 2.0.")
        
        # Click submit
        page.click("button:has-text('Submit Inquiry to Pasha Dev')")
        page.wait_for_timeout(1000)
        
        # Verify success
        has_success = page.locator("text=Submission Confirmed").count() > 0
        print("Success banner visible:", has_success)
        
        page.screenshot(path="C:/Users/USER/.gemini/antigravity/brain/aca0c042-dc6e-4169-b99f-648e944b6bf8/web_screenshot_contact_success.png")
        browser.close()

if __name__ == "__main__":
    test()
