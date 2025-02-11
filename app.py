import json
from scraper.conf_data import conf_data
from scraper.get_categories_and_gender import get_all_category_slugs
from scraper.get_product_link import get_product_link
from scraper.scrape_product import scrape_product_data

import os

# Ensure output directory exists
output_dir = "/app/output"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "scraped_data8.json")


def save_to_json(data, file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)


unique_links = get_all_category_slugs()
api_url = "https://api.mytheresa.com/api"
base_url = "https://www.mytheresa.com"

scraped_results = []

for gender, slug in unique_links:
    cookies, headers, category_query, product_query = conf_data(gender.lower())
    print("Scraping for category:", slug)

    product_links = get_product_link(
        cookies=cookies,
        headers=headers,
        query=category_query,
        slug=f"/{slug}",
        base_url=base_url,
        page=1,
    )

    for product_link in product_links:
        print("Scraping product:", product_link)
        result = scrape_product_data(
            cookies=cookies,
            headers=headers,
            query=product_query,
            url=product_link,
            gender=gender,
        )

        if result:  # Ensure result is not None
            scraped_results.append(result)

        # Save every 10 results
        if len(scraped_results) >= 10:
            save_to_json(scraped_results, output_file)
            print(f"Saved {len(scraped_results)} records to {output_file}")
            scraped_results = []  # Reset the list after saving

# Save any remaining records (if not a multiple of 10)
if scraped_results:
    save_to_json(scraped_results, output_file)
    print(f"Saved remaining {len(scraped_results)} records to {output_file}")

