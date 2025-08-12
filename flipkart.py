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


class Flipkart(BaseScraper):
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

            await page.goto("https://www.flipkart.com/", timeout=15000)
            await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
            await asyncio.sleep(random.uniform(1, 2))

            try:
                close_button = page.locator("button._2KpZ6l._2doB4z")
                if await close_button.is_visible(timeout=5000):
                    await close_button.click()
            except:
                pass

            search_box = page.locator("input.Pke_EE")
            await search_box.wait_for(timeout=15000)
            await search_box.click()
            await search_box.type(self.query, delay=200)
            await page.keyboard.press("Enter")

            await page.wait_for_selector("div._75nlfW", timeout=15000)
            product_cards = await page.locator("div._75nlfW").all()

            for card in product_cards[:3]:
                try:
                    if await card.locator("div.KzDlHZ, a.wjcEIp").first.is_visible():
                        name = await card.locator(
                            "div.KzDlHZ, a.wjcEIp"
                        ).first.inner_text()
                    else:
                        brand = await card.locator("div.syl9yP").inner_text()
                        model = await card.locator(
                            "a.WKTcLC, a.WKTcLC.BwBZTg"
                        ).inner_text()
                        name = f"{brand} {model}"

                    try:
                        price = await card.locator(
                            "div.Nx9bqj, div.Nx9bqj._4b5DiR"
                        ).first.inner_text()
                    except:
                        price = "N/A"

                    try:
                        rating = await card.locator("div.XQDdHH").inner_text()
                    except:
                        rating = "N/A"

                    try:
                        relative_link = await card.locator(
                            "a.CGtC98, a.wjcEIp"
                        ).first.get_attribute("href")
                        link = (
                            f"https://www.flipkart.com{relative_link}"
                            if relative_link
                            else "N/A"
                        )
                    except:
                        link = "N/A"

                    self.results.append(
                        {
                            "site": "Flipkart",
                            "name": name.strip(),
                            "price": price.strip(),
                            "rating": rating.strip(),
                            "link": link.strip(),
                        }
                    )

                except Exception as error:
                    print(f"Error extracting product from Flipkart: {error}")
                    continue

            return self.results, context

        except Exception as e:
            print(f"Flipkart scraper failed: {e}")
            return [], None
