import pyppeteer
import os

# Set the path to your local Chromium browser
os.environ["PYPPETEER_BROWSER"] = "C:\chrome-win\chrome.exe"
os.environ["PYPPETEER_SKIP_CHROMIUM_DOWNLOAD"] = "True"

async def render_page():
    browser = await pyppeteer.launch(executablePath=os.environ["PYPPETEER_BROWSER"], headless=True)
    page = await browser.newPage()
    await page.goto("https://sspai.com/post/96326")
    content = await page.content()  # Get the rendered content
    print(content)  # Print the rendered HTML
    await browser.close()

import asyncio
asyncio.get_event_loop().run_until_complete(render_page())
