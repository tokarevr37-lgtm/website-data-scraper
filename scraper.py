import csv
import time
import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
OUTPUT_FILE = "books_data.csv"


def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text


def parse_books(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for item in soup.select(".product_pod"):
        title = item.select_one("h3 a")["title"]
        price = item.select_one(".price_color").get_text(strip=True)
        availability = item.select_one(".availability").get_text(strip=True)

        books.append({
            "title": title,
            "price": price,
            "availability": availability
        })

    return books


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "price", "availability"])
        writer.writeheader()
        writer.writerows(data)


def main():
    print("Starting scraper...")

    html = get_page(URL)
    books = parse_books(html)

    save_to_csv(books, OUTPUT_FILE)

    print(f"Done. Saved {len(books)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
