import os
import asyncio
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright

START_URL = "https://www.connecticutchildrens.org/medical-professionals/clinical-pathways"
BASE_URL = "https://www.connecticutchildrens.org"
OUTPUT_FOLDER = "data"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


async def extract_links(page):
    """Extract all fully-qualified links AFTER the page hydrates."""
    await page.wait_for_load_state("networkidle")

    return [
        urljoin(page.url, href)
        for href in await page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.getAttribute('href'))"
        )
        if href
    ]


async def find_pdf_links(page, url):
    await page.goto(url)
    links = await extract_links(page)
    return [l for l in links if l.lower().endswith(".pdf")]


async def find_sections(page):
    await page.goto(START_URL)
    links = await extract_links(page)
    return [
        l for l in links
        if "/clinical-pathways/" in l
        and urlparse(l).netloc == urlparse(BASE_URL).netloc
    ]


async def download_pdf(page, pdf_url):
    filename = pdf_url.split("/")[-1]
    path = os.path.join(OUTPUT_FOLDER, filename)

    if os.path.exists(path):
        print(f"Already exists: {filename}")
        return

    print(f"Downloading: {filename}")

    async with page.expect_download() as dl:
        await page.goto(pdf_url)

    download = await dl.value
    await download.save_as(path)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Collecting sections...")
        sections = list(set(await find_sections(page)))
        print(f"Found {len(sections)} sections.")

        total = 0
        for section in sections:
            print(f"\nSection: {section}")
            pdfs = await find_pdf_links(page, section)
            print(f"PDFs found: {pdfs}")

            for pdf in pdfs:
                await download_pdf(page, pdf)
                total += 1

        print("\nDone.")
        print(f"Total processed PDFs: {total}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
