import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:5173")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'Log in' button to open the login modal.
        # Log in button
        elem = page.get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Select 'Industry representative' from the 'I am logging in as…' dropdown in the login modal.
        # Student Academician / Faculty University... dropdown
        elem = page.get_by_role("combobox")
        await elem.click(timeout=10000)
        
        # -> Select 'Industry representative' from the 'I am logging in as…' dropdown, fill the email and password fields, and click the 'Log in' button.
        # Student Academician / Faculty University... dropdown
        elem = page.locator("xpath=/html/body/div/div[2]/div[2]/form/div/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # -> Select 'Industry representative' from the 'I am logging in as…' dropdown, fill the email and password fields, and click the 'Log in' button.
        # you@university.edu email field
        elem = page.get_by_role("textbox", name="you@university.edu")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("recruitment@adoratech.io")
        
        # -> Select 'Industry representative' from the 'I am logging in as…' dropdown, fill the email and password fields, and click the 'Log in' button.
        # •••••••• password field
        elem = page.get_by_role("textbox", name="••••••••")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Password123!")
        
        # -> Select 'Industry representative' from the 'I am logging in as…' dropdown, fill the email and password fields, and click the 'Log in' button.
        # Log in button
        elem = page.locator("form").get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Click the '+ Post new opportunity' button to open the posting creation form.
        # + Post new opportunity button
        elem = page.get_by_role("button", name="+ Post new opportunity")
        await elem.click(timeout=10000)
        
        # -> Select 'Internship' from the 'Type' dropdown in the posting form.
        # Full-time Job Internship Project Apprenticeship dropdown
        elem = page.locator("xpath=/html/body/div/div/div/main/div/div[3]/form/div[3]/div/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # -> Fill 'Role Title', 'Required Skills (comma separated)', and 'Description' fields and click the 'Publish Role' button to submit the new posting.
        # e.g. Cloud Engineer Associate text field
        elem = page.get_by_role("textbox", name="e.g. Cloud Engineer Associate")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Automation Test Intern")
        
        # -> Fill 'Role Title', 'Required Skills (comma separated)', and 'Description' fields and click the 'Publish Role' button to submit the new posting.
        # e.g. Python, Docker, AWS text field
        elem = page.get_by_role("textbox", name="e.g. Python, Docker, AWS")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("React, JavaScript, Testing")
        
        # -> Fill 'Role Title', 'Required Skills (comma separated)', and 'Description' fields and click the 'Publish Role' button to submit the new posting.
        # Role responsibilities and requirements… text area
        elem = page.get_by_role("textbox", name="Role responsibilities and")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("This is a test posting created by automated QA.")
        
        # -> Fill 'Role Title', 'Required Skills (comma separated)', and 'Description' fields and click the 'Publish Role' button to submit the new posting.
        # Publish Role button
        elem = page.get_by_role("button", name="Publish Role")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The newly created posting 'Automation Test Intern' is visible in the Open roles list.
        # Assert-outcome: passed
        # Assert: Verify the posting title 'Automation Test Intern' appears in the Open roles list.
        await expect(page.locator("#root").nth(0)).to_contain_text("Automation Test Intern", timeout=15000), "Verify the posting title 'Automation Test Intern' appears in the Open roles list."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    