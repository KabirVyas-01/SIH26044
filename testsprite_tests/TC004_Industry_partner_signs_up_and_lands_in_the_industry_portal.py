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
        
        # -> Click the 'Log in' button to open the authentication flow.
        # Log in button
        elem = page.get_by_role("button", name="Log in")
        await elem.click(timeout=10000)
        
        # -> Click the 'Register' link in the login modal to open the registration flow.
        # Register button
        elem = page.locator("form").get_by_role("button", name="Register")
        await elem.click(timeout=10000)
        
        # -> Select 'Industry representative' from the 'I am registering as…' dropdown in the Create your account form.
        # Student Academician / Faculty University... dropdown
        elem = page.locator("form div").filter(has_text="I am registering as…").get_by_role("combobox")
        await elem.click(timeout=10000)
        
        # -> Select 'Industry representative' from the 'I am registering as…' dropdown in the Create your account modal.
        # Student Academician / Faculty University... dropdown
        elem = page.locator("xpath=/html/body/div/div[2]/div[2]/form/div/select").nth(0)
        await elem.wait_for(state="visible", timeout=10000)
        await elem.select_option("")
        
        # -> Fill the 'Company Name', 'Official Email', and 'Choose Password' fields with industry partner details and click the 'Continue (Send OTP)' button.
        # Adora Technologies text field
        elem = page.get_by_role("textbox", name="Adora Technologies")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Adora Technologies")
        
        # -> Fill the 'Company Name', 'Official Email', and 'Choose Password' fields with industry partner details and click the 'Continue (Send OTP)' button.
        # you@university.edu or name@company.com email field
        elem = page.get_by_role("textbox", name="you@university.edu or name@")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("recruitment@adoratech.io")
        
        # -> Fill the 'Company Name', 'Official Email', and 'Choose Password' fields with industry partner details and click the 'Continue (Send OTP)' button.
        # •••••••• password field
        elem = page.get_by_role("textbox", name="••••••••")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("Password123!")
        
        # -> Fill the 'Company Name', 'Official Email', and 'Choose Password' fields with industry partner details and click the 'Continue (Send OTP)' button.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button to populate the OTP, then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button to populate the OTP, then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # ← Back to change details button
        elem = page.get_by_role("button", name="← Back to change details")
        await elem.click(timeout=10000)
        
        # -> Click the 'Continue (Send OTP)' button to send/trigger OTP verification and open the verification modal.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Verify & Create Account button
        elem = page.get_by_role("button", name="Verify & Create Account")
        await elem.click(timeout=10000)
        
        # -> Click the '← Back to change details' button to return to the registration form so the official email can be changed.
        # ← Back to change details button
        elem = page.get_by_role("button", name="← Back to change details")
        await elem.click(timeout=10000)
        
        # -> Fill the 'Official Email' field with a new unique industry email and submit by clicking the 'Continue (Send OTP)' button.
        # you@university.edu or name@company.com email field
        elem = page.get_by_role("textbox", name="you@university.edu or name@")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("recruitment+automation123@adoratech.io")
        
        # -> Fill the 'Official Email' field with a new unique industry email and submit by clicking the 'Continue (Send OTP)' button.
        # Continue (Send OTP) button
        elem = page.get_by_role("button", name="Continue (Send OTP)")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Auto-fill button
        elem = page.get_by_role("button", name="Auto-fill")
        await elem.click(timeout=10000)
        
        # -> Click the 'Auto-fill' button then click the 'Verify & Create Account' button to submit the OTP and complete registration.
        # Verify & Create Account button
        elem = page.get_by_role("button", name="Verify & Create Account")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> User is routed to the Industry portal and the industry dashboard is visible.
        # Assert-outcome: passed
        # Assert: URL contains '#industry', indicating the industry route.
        await expect(page).to_have_url(re.compile("\\#industry"), timeout=15000), "URL contains '#industry', indicating the industry route."
        await page.get_by_role("button", name="Dashboard").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The 'Dashboard' link is visible in the left navigation, indicating the industry dashboard layout.
        await expect(page.get_by_role("button", name="Dashboard").nth(0)).to_be_visible(timeout=15000), "The 'Dashboard' link is visible in the left navigation, indicating the industry dashboard layout."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    