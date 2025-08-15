import asyncio
import re
from collections import defaultdict
from playwright.async_api import async_playwright
from rapidfuzz import fuzz, process

from amazon import Amazon
from flipkart import Flipkart
from croma import Croma
from reliance_digital import RelianceDigital


# I used a Function to clean and normalize text for better matching
def preprocess(text):
    text = text.lower()
    # used to Remove storage sizes (GB, TB), RAM sizes (e.g., 8GB, 16gb)
    text = re.sub(r"\b\d+\s?(gb|tb)\b", "", text)
    colors = [
        "black",
        "white",
        "blue",
        "red",
        "green",
        "yellow",
        "silver",
        "gold",
        "grey",
        "gray",
        "purple",
        "pink",
        "orange",
        "beige",
        "cyan",
        "magenta",
    ]
    pattern = r"\b(" + "|".join(colors) + r")\b"
    text = re.sub(pattern, "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def scrape_product(query):
    MIN_MATCH_SCORE = 60
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        scrapers = [
            Amazon(query),
            Flipkart(query),
            Croma(query),
            RelianceDigital(query),
        ]

        # Run all scrapers simultaneously
        results_with_contexts = await asyncio.gather(
            *(scraper.scrape(browser) for scraper in scrapers), return_exceptions=True
        )

        all_products = []
        contexts = []

        for result in results_with_contexts:
            if isinstance(result, Exception):
                print(f"Scraper failed: {result}")
                continue

            site_result, context = result

            if isinstance(site_result, list):
                all_products.extend(site_result)

            if context:
                contexts.append(context)

        for ctx in contexts:
            try:
                await ctx.close()
            except:
                pass

        if not all_products:
            print("No results found.")
            return

        # Group results by site
        grouped = defaultdict(list)
        for product in all_products:
            grouped[product.get("site", "Unknown")].append(product)

        # Best match from each site
        for site, products in grouped.items():
            names = [p["name"] for p in products]

            # Apply preprocessing before matching
            preprocessed_names = [preprocess(name) for name in names]
            preprocessed_query = preprocess(query)

            best_match = process.extractOne(
                preprocessed_query, preprocessed_names, scorer=fuzz.token_set_ratio
            )

            if not best_match:
                print(f"No match found for {site}")
                continue

            match_name_cleaned, score, idx = best_match
            match_name_original = names[idx]  # Get original name from index

            # It'll Skip if score is below threshold
            if score < MIN_MATCH_SCORE:
                print(f"⚠️ Low match score ({score}) for {site} — No Products Found")
                continue

            best_product = next(
                (p for p in products if p["name"] == match_name_original), None
            )

            if best_product:
                results.append(
                    {
                        "site": site,
                        "name": best_product["name"],
                        "price": best_product["price"],
                        "rating": best_product["rating"],
                        "link": best_product["link"],
                    }
                )
    return results


# CLI entry point
async def cli_main():
    query = input("Enter product to search: ")
    results = await scrape_product(query)
    if not results:
        print("No results found.")
    else:
        for r in results:
            print(f"\nBest match from {r['site']}")
            print(f"Name: {r['name']}")
            print(f"Price: {r['price']}")
            print(f"Rating: {r['rating']}")
            print(f"Link: {r['link']}")
            print("-" * 50)


if __name__ == "__main__":
    asyncio.run(cli_main())
