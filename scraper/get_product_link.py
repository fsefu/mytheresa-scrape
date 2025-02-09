import requests


def get_product_link(cookies, headers, query, slug, base_url, page=1):
    payload = {
        "query": query,
        "variables": {
            "categories": [],
            "colors": [],
            "designers": [],
            "fta": None,
            "page": page,
            "patterns": [],
            "reductionRange": [],
            "saleStatus": None,
            "size": 120,
            "sizesHarmonized": [],
            "slug": slug,
            "sort": None,
        },
    }
    # print("payload: ", payload)
    response = requests.post(
        "https://api.mytheresa.com/api", cookies=cookies, headers=headers, json=payload
    )
    print(f"scraping for {slug} page={page}")
    json_response = response.json()
    data = json_response.get("data", {}).get("xProductListingPage", {})
    products_urls = []
    if data:
        products = data.get("products", [])
        for product in products:
            product_url = f"{base_url}/fr/en/modele/{product['slug']}"
            products_urls.append(product_url)

        pagination = data.get("pagination", {})
        current_page = pagination.get("currentPage")
        total_pages = pagination.get("totalPages")
        if current_page < total_pages:
            return get_product_link(
                cookies=cookies,
                headers=headers,
                query=query,
                slug=slug,
                base_url=base_url,
                page=current_page + 1,
            )

    return products_urls
