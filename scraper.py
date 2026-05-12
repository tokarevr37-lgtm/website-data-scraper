import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
CSV_FILE = "books_data.csv"
EXCEL_FILE = "books_data.xlsx"
MAX_PAGES = 3


def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def parse_books(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for item in soup.select(".product_pod"):
        title = item.select_one("h3 a")["title"]
        price = item.select_one(".price_color").get_text(strip=True)
        availability = item.select_one(".availability").get_text(strip=True)
        rating = item.select_one("p.star-rating")["class"][1]

        books.append({
            "title": title,
            "price": price,
            "availability": availability,
            "rating": rating
        })

    return books


def save_to_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "price", "availability", "rating"]
        )
        writer.writeheader()
        writer.writerows(data)


def save_to_excel(data, filename):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Books Data"

    headers = ["Title", "Price", "Availability", "Rating"]
    sheet.append(headers)

    for book in data:
        sheet.append([
            book["title"],
            book["price"],
            book["availability"],
            book["rating"]
        ])

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))

        sheet.column_dimensions[column_letter].width = max_length + 2

    workbook.save(filename)


def main():
    all_books = []

    print("Starting website data scraper...")

    for page in range(1, MAX_PAGES + 1):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}: {url}")

        try:
            html = fetch_page(url)
            books = parse_books(html)
            all_books.extend(books)
            time.sleep(1)

        except requests.RequestException as error:
            print(f"Failed to scrape page {page}: {error}")

    if not all_books:
        print("No data collected.")
        return

    save_to_csv(all_books, CSV_FILE)
    save_to_excel(all_books, EXCEL_FILE)

    print(f"Done. Collected {len(all_books)} records.")
    print(f"CSV saved to: {Path(CSV_FILE).resolve()}")
    print(f"Excel saved to: {Path(EXCEL_FILE).resolve()}")


if __name__ == "__main__":
    main()
