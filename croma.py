import random
import asyncio
from config import USER_AGENT, LOCALE, VIEW_PORT, TIME_ZONE_ID, EXTRA_HTTP_HEADERS
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, query):
        self.query = query
        self.results = []

    @abstractmethod
    async def scrape(self, browser):
        pass


class Croma(BaseScraper):
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

            await page.goto("https://www.croma.com/", timeout=15000)
            await asyncio.sleep(random.uniform(1, 2))

            search_bar = page.get_by_role("textbox", name="What are you looking for ?")
            await search_bar.wait_for(timeout=8000)
            await search_bar.click()
            await search_bar.type(self.query, delay=150)
            await page.keyboard.press("Enter")

            await asyncio.sleep(2)
            await page.mouse.move(random.randint(0, 500), random.randint(0, 500))

            try:
                await page.wait_for_selector(
                    'div[data-testid="product-id"]', timeout=10000
                )
            except Exception as e:
                print(f" Timeout or selector error: {e}")
                await browser.close()
                return []

            product_cards = await page.locator('div[data-testid="product-id"]').all()

            if not product_cards:
                print("No product cards found.")
                # self.results.append(
                #   {
                #      "site": "Croma",
                #        "name": "No products found",
                #        "price": "N/A",
                #        "rating": "N/A",
                #        "link": "N/A",
                #    }
                # )
                return self.results, context

            for card in product_cards[:3]:
                try:
                    name = await card.locator(
                        'div[class="plp-prod-title-rating-cont"]'
                    ).inner_text()
                except:
                    name = "N/A"

                try:
                    price = await card.locator(
                        'span[data-testid="new-price"]'
                    ).inner_text()
                except:
                    price = "N/A"

                try:
                    rating_elem = card.locator('span[class="rating-text"]')
                    rating = (
                        await rating_elem.inner_text()
                        if await rating_elem.is_visible()
                        else "N/A"
                    )
                except:
                    rating = "N/A"

                try:
                    relative_link = await card.locator(
                        'a[rel="noopener noreferrer"]'
                    ).get_attribute("href")
                    link = (
                        f"https://www.croma.com{relative_link}"
                        if relative_link
                        else "N/A"
                    )
                except:
                    link = "N/A"

                self.results.append(
                    {
                        "site": "Croma",
                        "name": name.strip(),
                        "price": price.strip(),
                        "rating": rating.strip(),
                        "link": link.strip(),
                    }
                )

            return self.results, context

        except Exception as e:
            print(f"Croma scraper failed: {e}")
            return [], None
