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
        
        # -> Click the 'Register' button to open the registration/authentication modal
        # Register button
        elem = page.get_by_role("button", name="Register")
        await elem.click(timeout=10000)
        
        # -> Click the 'Continue (Send OTP)' button after filling Full Name, Official Email, and Password to submit the registration form.
        # Kareena Kapoor text field
        elem = page.get_by_role("textbox", name="Kareena Kapoor")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("QA Student")
        
        # -> Click the 'Continue (Send OTP)' button after filling Full Name, Official Email, and Password to submit the registration form.
        # you@university.edu or name@company.com email field
        elem = page.get_by_role("textbox", name="you@university.edu or name@")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("qa.student+autotest@college.edu")
        
        # -> Click the 'Continue (Send OTP)' button after filling Full Name, Official Email, and Password to submit the registration form.
        # •••••••• password field
        elem = page.get_by_role("textbox", name="••••••••")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Password123!")
        
        # -> Click the 'Continue (Send OTP)' button after filling Full Name, Official Email, and Password to submit the registration form.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button, then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button, then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # button
        elem = page.locator("div").filter(has_text=re.compile(r"^Verify your email$")).get_by_role("button")
        await elem.click(timeout=10000)
        
        # -> Click the 'Log in' button to open the login modal so the registered student credentials can be tested.
        # Log in button
        elem = page.get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Click the 'Log in' button in the login modal to submit the credentials and verify navigation to the student portal.
        # Log in button
        elem = page.locator("form").get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Click the 'Log in' button in the login modal to submit qa.student+autotest@college.edu / Password123! and verify whether the student portal loads.
        # Log in button
        elem = page.locator("form").get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Open the Register modal by clicking the 'Register' button so the registration form fields can be inspected.
        # Register button
        elem = page.locator("form").get_by_role("button", name="Register")
        await elem.click(timeout=10000)
        
        # -> Click the 'Continue (Send OTP)' button to send the OTP and proceed to the verification step.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button and then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button and then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # ← Back to change details button
        elem = page.get_by_role("button", name="← Back to change details")
        await elem.click(timeout=10000)
        
        # -> Click the 'Continue (Send OTP)' button to send the OTP and open the verification modal.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Verify & Create Account button
        elem = page.get_by_role("button", name="Verify & Create Account")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button, then click the 'Verify & Create Account' button to submit the Demo OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button, then click the 'Verify & Create Account' button to submit the Demo OTP and complete registration.
        # Verify & Create Account button
        elem = page.get_by_role("button", name="Verify & Create Account")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Student portal is displayed (navigated to #student and the 'Overview' navigation is visible).
        # Assert-outcome: passed
        # Assert: URL contains '#student', indicating the student route.
        await expect(page).to_have_url(re.compile("\\#student"), timeout=15000), "URL contains '#student', indicating the student route."
        await page.get_by_role("button", name="Overview").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The 'Overview' navigation button is visible in the student portal.
        await expect(page.get_by_role("button", name="Overview").nth(0)).to_be_visible(timeout=15000), "The 'Overview' navigation button is visible in the student portal."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    