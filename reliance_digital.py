import random
import asyncio
from config import USER_AGENT, LOCALE, VIEW_PORT, TIME_ZONE_ID, EXTRA_HTTP_HEADERS
from abc import ABC, abstractmethod
from base import BaseScraper


class RelianceDigital(BaseScraper):
    async def scrape(self, browser):
        try:
            context = await browser.new_context(
                user_agent=USER_AGENT,
                locale=LOCALE,
                viewport=VIEW_PORT,
                timezone_id=TIME_ZONE_ID,
                extra_http_headers=EXTRA_HTTP_HEADERS,
            )

            page = await context.new_page()
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )

            await page.goto("https://www.reliancedigital.in/", timeout=15000)
            await asyncio.sleep(random.uniform(1, 2))

            try:
                notif = page.get_by_text(
                    "Don't miss on important updates.We'll only send you relevant content and"
                )
                if await notif.is_visible():
                    await page.get_by_role("button", name="No, don't.").click()
            except:
                pass

            search_box = page.get_by_role("textbox", name="Search Products & Brands")
            await search_box.wait_for(timeout=8000)
            await search_box.click()
            await search_box.type(self.query, delay=150)
            await page.keyboard.press("Enter")

            await asyncio.sleep(2)
            await page.mouse.move(random.randint(0, 500), random.randint(0, 500))

            await asyncio.sleep(2)
            await page.mouse.move(random.randint(0, 500), random.randint(0, 500))

            try:
                await page.wait_for_selector('div[class="product-card"]', timeout=10000)
            except Exception as e:
                print(f"Timeout or selector error: {e}")
                await browser.close()
                return []

            product_cards = await page.locator('div[class="product-card"]').all()
            print(f" Found {len(product_cards)} products")

            if not product_cards:
                print("No product cards found.")
                await browser.close()
                return []

            print("⌛ Extracting all products...")

            for card in product_cards[:3]:
                try:
                    name = await card.locator(
                        'div[class="product-card-title"]'
                    ).inner_text()
                except:
                    name = "N/A"

                try:
                    price = await card.locator('div[class="price"]').inner_text()
                except:
                    price = "N/A"

                rating = "N/A"

                try:
                    relative_link = await card.locator(
                        'a[class="details-container"]'
                    ).get_attribute("href")
                    link = (
                        f"https://www.reliancedigital.in/{relative_link}"
                        if relative_link
                        else "N/A"
                    )
                except:
                    link = "N/A"

                try:
                    image_url = await card.locator(
                        'a[class="product-card-image"]'
                    ).get_attribute("srcset")
                    if not image_url:
                        image_url = await card.locator(
                            'a[class="product-card-image"]'
                        ).get_attribute("src")

                    if not image_url:
                        image_url = "N/A"
                    else:
                        # srcset can contain multiple URLs like "url1 1x, url2 2x"
                        # we just take the first one
                        image_url = image_url.split(",")[0].split()[0]
                except:
                    image_url = "N/A"

                self.results.append(
                    {
                        "site": "Reliance Digital",
                        "name": name.strip(),
                        "price": price.strip(),
                        "rating": rating,
                        "link": link.strip(),
                        "image": image_url.strip(),
                    }
                )

            return self.results, context

        except Exception as e:
            print(f"Reliance Digital scraper failed: {e}")
            return [], None
