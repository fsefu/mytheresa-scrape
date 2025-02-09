import requests
import xml.etree.ElementTree as ET
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_sitemap_urls(sitemap_index_url):
    print("extracting sitemap ", sitemap_index_url)
    """Fetch and parse the sitemap index to extract all sitemap URLs."""
    response = requests.get(sitemap_index_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {sitemap_index_url}")
        return []

    sitemap_index = ET.fromstring(response.content)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [
        loc.text for loc in sitemap_index.findall("sm:sitemap/sm:loc", namespace)
    ]
    return sitemap_urls


def get_urls_from_sitemap(sitemap_url):
    print("getting urls from sitemap with url: ", sitemap_url)
    """Fetch and parse a sitemap (XML or TXT) to extract URLs."""
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        print(f"Failed to retrieve {sitemap_url}")
        return []

    urls = []
    if sitemap_url.endswith(".xml"):
        # Parse XML sitemap
        sitemap = ET.fromstring(response.content)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in sitemap.findall("sm:url/sm:loc", namespace)]
    elif sitemap_url.endswith(".txt"):
        # Parse TXT sitemap (one URL per line)
        urls = response.text.splitlines()

    return urls


def filter_fr_en_urls(urls):
    """Filter URLs to only include those containing '/fr/en/'."""
    return [url for url in urls if "/fr/en/" in url]


def exclude_p_number_urls(urls):
    pattern = re.compile(r"-p\d+")
    return [url for url in urls if not pattern.search(url)]


def extract_category_slugs(urls):
    """Extract gender and slug from URLs containing '/fr/en/' and '-p' followed by a number."""
    unique_links = set()
    for url in urls:
        if "/women/" in url:
            gender = "women"
        elif "/men/" in url:
            gender = "men"
        elif "/kids/" in url:
            gender = "kids"
        else:
            continue

        parts = url.split("/")
        gender_index = parts.index(gender)
        slug = "/".join(parts[gender_index + 1 :])
        unique_links.add((gender, slug))

    return unique_links


def get_categories_and_gender():
    unique_links = set()
    # List of URLs to scrape
    base_urls = [
        "https://www.mytheresa.com/fr/en/women",
        "https://www.mytheresa.com/fr/en/men",
        "https://www.mytheresa.com/fr/en/kids",
    ]

    # Regular expression to match URLs containing '-p' followed by a number
    pattern = r"-p\d+$"  # Ensure '-p' is followed by digits until the end of the string

    for base_url in base_urls:
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"Failed to retrieve {base_url}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        root_div = soup.find("div", id="root")
        if not root_div:
            print(f"No 'root' div found in {base_url}")
            continue

        for link in root_div.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            # Skip URLs that contain '-p' followed directly by a number
            if re.search(pattern, href):
                continue

            # Skip links that end with a number (after removing trailing slashes)
            if href.rstrip("/").split("/")[-1].isdigit():
                continue

            # Check if the link contains the gender segment
            if "/women/" in full_url:
                gender = "women"
            elif "/men/" in full_url:
                gender = "men"
            elif "/kids/" in full_url:
                gender = "kids"
            else:
                continue

            # Extract the slug after the gender segment
            parts = full_url.split("/")
            gender_index = parts.index(gender)
            slug = "/".join(parts[gender_index + 1 :])

            unique_links.add((gender, slug))

    return unique_links


def get_all_category_slugs():
    """Fetch all sitemaps, extract URLs, filter for '/fr/en/' and '-p' followed by a number, and extract slugs."""
    sitemap_index_url = "https://www.mytheresa.com/sitemap.xml"
    sitemap_urls = get_sitemap_urls(sitemap_index_url)

    all_filtered_urls = []
    for sitemap_url in sitemap_urls:
        urls = get_urls_from_sitemap(sitemap_url)

        filtered_urls = filter_fr_en_urls(urls)
        filtered_urls = exclude_p_number_urls(filtered_urls)
        all_filtered_urls.extend(filtered_urls)

    unique_links_from_sitemap = extract_category_slugs(all_filtered_urls)
    unique_links_from_html = get_categories_and_gender()

    # Combine results from both methods
    unique_links = unique_links_from_sitemap.union(unique_links_from_html)
    return unique_links


# def save_to_json(data, filename):
#     """Save data to a JSON file."""
#     with open(filename, "w") as f:
#         json.dump(list(data), f, indent=4)


# if __name__ == "__main__":
#     unique_links = get_all_category_slugs()
#     print("total links ", len(unique_links))
#     save_to_json(unique_links, "filtered_urls3.json")
#     print("Filtered URLs saved to 'filtered_urls.json'")

# import requests
# import re
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin


# def get_categories_and_gender():
#     unique_links = set()
#     # List of URLs to scrape
#     base_urls = [
#         "https://www.mytheresa.com/fr/en/women",
#         "https://www.mytheresa.com/fr/en/men",
#         "https://www.mytheresa.com/fr/en/kids",
#     ]

#     # Regular expression to match URLs containing '-p' followed by a number
#     pattern = r"-p\d+$"  # Ensure '-p' is followed by digits until the end of the string

#     for base_url in base_urls:
#         response = requests.get(base_url)
#         if response.status_code != 200:
#             print(f"Failed to retrieve {base_url}")
#             continue

#         soup = BeautifulSoup(response.content, "html.parser")
#         root_div = soup.find("div", id="root")
#         if not root_div:
#             print(f"No 'root' div found in {base_url}")
#             continue

#         for link in root_div.find_all("a", href=True):
#             href = link["href"]
#             full_url = urljoin(base_url, href)

#             # Skip URLs that contain '-p' followed directly by a number
#             if re.search(pattern, href):
#                 continue

#             # Skip links that end with a number (after removing trailing slashes)
#             if href.rstrip("/").split("/")[-1].isdigit():
#                 continue

#             # Check if the link contains the gender segment
#             if "/women/" in full_url:
#                 gender = "women"
#             elif "/men/" in full_url:
#                 gender = "men"
#             elif "/kids/" in full_url:
#                 gender = "kids"
#             else:
#                 continue

#             # Extract the slug after the gender segment
#             parts = full_url.split("/")
#             gender_index = parts.index(gender)
#             slug = "/".join(parts[gender_index + 1 :])

#             unique_links.add((gender, slug))

#     return unique_links


# # unique_links = get_categories_and_gender()

# # # Print the results
# # for gender, slug in unique_links:
# #     print(f"Gender: {gender}, Slug: {slug}")

# # print("total results: ", len(unique_links))
