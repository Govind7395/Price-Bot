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


class Amazon(BaseScraper):
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

            await page.goto("https://www.amazon.in/", wait_until="domcontentloaded")
            await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
            await asyncio.sleep(random.uniform(1, 2))

            try:
                close_button = page.locator('button[class="a-button-text"]')
                if await close_button.is_visible():
                    await close_button.click()
            except:
                pass

            search_box = page.get_by_role("searchbox", name="Search Amazon.in")
            await page.mouse.move(random.randint(200, 700), random.randint(200, 500))
            await search_box.click()
            await search_box.type(self.query, delay=500)
            await page.keyboard.press("Enter")

            await page.wait_for_selector(
                'div[data-component-type="s-search-result"]', timeout=10000
            )

            await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
            await asyncio.sleep(random.uniform(1, 2))

            product_cards = await page.locator(
                'div[data-component-type="s-search-result"]'
            ).all()

            if not product_cards:
                print("No product cards found.")
                await browser.close()
                return []

            print(f"Found {len(product_cards)} product cards.")

            count = 0
            for card in product_cards:
                if count >= 10:
                    break

                # Skip sponsored products
                if await card.locator("span.s-sponsored-label-text").count() > 0:
                    continue

                try:
                    title_candidate = card.locator("span#productTitle")
                    if await title_candidate.count() == 0:
                        title_candidate = card.locator("h2 span")

                    if await title_candidate.count() > 0:
                        name = await title_candidate.first.inner_text()
                    else:
                        alt_title = card.locator("a span")
                        if await alt_title.count() > 0:
                            name = await alt_title.first.inner_text()
                        else:
                            name = "N/A"

                    try:
                        price = await card.locator("span.a-price-whole").inner_text()
                    except:
                        price = "N/A"

                    try:
                        rating_element = card.locator(
                            "a.a-popover-trigger.a-declarative"
                        )
                        if await rating_element.count() > 0:
                            rating_text = (
                                await rating_element.get_attribute("aria-label") or ""
                            )
                            rating = rating_text.split(" ")[0] if rating_text else "N/A"
                        else:
                            rating = "N/A"
                    except:
                        rating = "N/A"

                    try:
                        link_elem = await card.locator(
                            "a.a-link-normal"
                        ).first.get_attribute("href")
                        link = f"https://www.amazon.in{link_elem}"
                    except:
                        link = "N/A"

                    self.results.append(
                        {
                            "site": "Amazon",
                            "name": name.strip(),
                            "price": price.strip() if isinstance(price, str) else price,
                            "rating": rating,
                            "link": link,
                        }
                    )

                    count += 1

                except Exception as error:
                    print(f"Error extracting product: {error}")
                    continue

            return self.results, context

        except Exception as e:
            print(f"Amazon scraper failed: {e}")
            return [], None
