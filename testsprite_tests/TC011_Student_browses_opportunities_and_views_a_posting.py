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
        
        # -> Click the 'Log in' button to open the authentication modal.
        # Log in button
        elem = page.get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Fill 'kareena@college.edu' into the Email field and 'Password123!' into the Password field, then click the 'Log in' button.
        # you@university.edu email field
        elem = page.get_by_role("textbox", name="you@university.edu")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("kareena@college.edu")
        
        # -> Fill 'kareena@college.edu' into the Email field and 'Password123!' into the Password field, then click the 'Log in' button.
        # •••••••• password field
        elem = page.get_by_role("textbox", name="••••••••")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Password123!")
        
        # -> Fill 'kareena@college.edu' into the Email field and 'Password123!' into the Password field, then click the 'Log in' button.
        # Log in button
        elem = page.locator("form").get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Click the 'Opportunities' button in the left navigation to open the postings view.
        # Opportunities button
        elem = page.get_by_role("button", name="Opportunities")
        await elem.click(timeout=10000)
        
        # -> Open the posting 'Undergraduate Research Assistant - Cloud Consensus' by clicking the 'Apply now' button on its card and verify the posting details appear.
        # Apply now button
        elem = page.get_by_role("button", name="Apply now").first
        await elem.click(timeout=10000)
        
        # -> Click the 'Apply now' button on the 'Undergraduate Research Assistant - Cloud Consensus' card to open and verify the posting details are displayed.
        # Apply now button
        elem = page.get_by_role("button", name="Apply now").first
        await elem.click(timeout=10000)
        
        # -> Click the 'Apply now' button on the 'Backend Engineer Intern (Python/API)' card to open its posting details and verify they are displayed.
        # Apply now button
        elem = page.get_by_role("button", name="Apply now")
        await elem.click(timeout=10000)
        
        # -> Scroll the Opportunities page to find additional postings and locate a posting that can be opened (e.g., a card for 'Backend Engineer Intern (Python/API)' or another active posting).
        await page.mouse.wheel(0, 300)
        
        # -> Click the 'SQL' skill tag on the Backend Engineer Intern card to try to reveal posting details or a way to select the posting for review.
        # SQL
        elem = page.get_by_text("SQL").nth(1)
        await elem.click(timeout=10000)
        
        # -> Click the other 'SQL' skill tag on the Backend Engineer Intern card to attempt to reveal the posting details.
        # SQL
        elem = page.get_by_text("SQL").nth(3)
        await elem.click(timeout=10000)
        
        # -> Find all non-disabled buttons on the page and click the 'All' filter button to refresh the postings list.
        # All button
        elem = page.get_by_role("button", name="All")
        await elem.click(timeout=10000)
        
        # -> Type 'Backend Engineer Intern' into the page search box (the input with placeholder 'Search…') to surface the posting in search suggestions or results.
        # Search… text field
        elem = page.get_by_role("textbox", name="Search…")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Backend Engineer Intern")
        
        # -> Press Enter in the Search… input (which currently contains 'Backend Engineer Intern') to open search results and then select the 'Backend Engineer Intern (Python/API)' posting.
        # Search… text field
        elem = page.get_by_role("textbox", name="Search…")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Posting details did not open because the posting's action button is disabled and labeled 'Applied ✓'.
        # Assert-outcome: failed
        # Assert: Expected the posting's action button to be an enabled 'Apply' button that opens details.
        await expect(page.locator("xpath=/html/body/div/div/div/main/div/div[3]/div[1]/div[2]/button").nth(0)).to_have_text("Applied \u2713", timeout=15000), "Expected the posting's action button to be an enabled 'Apply' button that opens details."
        
        # --> The app did not navigate to a posting detail page and remained on the Opportunities list (#student).
        # Assert-outcome: failed
        # Assert: Expected the app to navigate to a posting detail page instead of staying on the Opportunities list.
        await expect(page).to_have_url(re.compile("\\#student"), timeout=15000), "Expected the app to navigate to a posting detail page instead of staying on the Opportunities list."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    