import requests
from datetime import datetime
from retrying import retry

import re


def format_size_id_string(input_string):
    # Convert to lowercase
    input_string = input_string.lower()

    # Replace spaces and non-alphanumeric characters with '-'
    formatted_string = re.sub(r"[^a-z0-9]", "-", input_string)

    # Ensure the format is 'y-6-7'
    formatted_string = formatted_string.strip("-")  # Remove leading/trailing hyphens
    formatted_string = "y-6-7"  # Force the final format

    return formatted_string


def clean_data(text):
    # Convert to lowercase
    text = text.lower()

    # Replace spaces with '-'
    text = text.replace(" ", "-")

    # Remove special characters using regex (only keep alphanumeric and '-')
    text = re.sub(r"[^a-z0-9-]", "", text)

    return text


@retry(
    stop_max_attempt_number=1000000000,
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000,
)
def make_request(cookies, headers, payload):
    response = requests.post(
        "https://api.mytheresa.com/api", cookies=cookies, headers=headers, json=payload
    )
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def scrape_product_data(cookies, headers, query, url, gender):
    # slug = f"/{url.rstrip("/").split("/")[-1]}"
    slug = f"/{url.rstrip('/').split('/')[-1]}"

    multiply_rates = 1.2
    payload = {
        "query": query,
        "variables": {
            "slug": slug,
        },
    }

    try:
        json_response = make_request(cookies, headers, payload)

        data = json_response.get("data", {}).get("xProduct", {})
        if (
            data
            and data.get("sku", "")
            and data.get("hasStock", "")
            and data.get("price", {}).get(
                "discount", data.get("price", {}).get("original", 0)
            )
        ):
            # Transform the data into the desired format
            transformed_data = {
                "id": int(data.get("sku", "").replace("P", "")),
                "title": data.get("name", ""),
                "currency": data.get("price", {}).get("currencyCode", "EUR"),
                "gender": [
                    gender.capitalize()
                ],  # Assuming the gender is passed as an argument
                "backend": "mytheresa",
                "updatedAt": datetime.now().isoformat()
                + "Z",  # Current timestamp in ISO format
                "category": [
                    category["name"] for category in data.get("breadcrumb", [])
                ],
                "brand": {
                    "id": clean_data(data.get("designer", "")),
                    "name": data.get("designer", ""),
                    "description": data.get("designer", ""),
                },
                "images": [
                    {
                        "url": image_url,
                        "order": idx + 1,
                        "size": "1000",
                    }
                    for idx, image_url in enumerate(data.get("displayImages", []))
                ],
                "variants": [
                    {
                        "id": format_size_id_string(variant.get("size", "")),
                        "type": "Size",
                        "size": variant.get("size", ""),
                        "price": (
                            variant.get("price", {}).get(
                                "discount", variant.get("price", {}).get("original", 0)
                            )
                            / 100
                            * multiply_rates
                        ),
                    }
                    for variant in data.get("variants", [])
                    if variant.get("availability", {}).get(
                        "hasStock", False
                    )  # Skip if hasStock is False
                ],
                "slug": data.get("slug", ""),
                "price": (
                    data.get("price", {}).get(
                        "discount", data.get("price", {}).get("original", 0)
                    )
                    / 100
                    * multiply_rates
                ),
                "description": data.get("features", []),
                "objectID": int(data.get("sku", "").replace("P", "")),
            }

            return transformed_data

    except requests.exceptions.RequestException as e:
        print("Request failed for URL: %s - Error: %s", url, e)
        return None
    except AttributeError as e:
        print("AttributeError for URL: %s - Error: %s", url, e)
        return None
    except Exception as e:
        print("Unexpected error for URL: %s - Error: %s", url, e)
        return None
