import asyncio
from functools import partial

from playwright.async_api import async_playwright

from config import init_pages

from communication.communication_user import CommunicationUser

from browser.handle_route import handle_route

from files.browser.store_res_to_disk import store_res_to_disk


async def run_browser(session_maker, comm_user: CommunicationUser):
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch(headless=False)
        context = await browser.new_context()

        await context.route("**/*", partial(
            handle_route,
            session_maker,
            comm_user
        ))
        context.on("response", partial(store_res_to_disk, session_maker))

        for page_url in init_pages:
            page = await context.new_page()

            await page.goto(page_url)

        try:
            while (
                browser.is_connected()
                and any((
                    True
                    for page in context.pages
                    if not page.is_closed()
                ))
            ):
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await context.close()
            await browser.close()
        except asyncio.CancelledError:
            await context.close()
            await browser.close()
