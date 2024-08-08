import os
import requests
from bs4 import BeautifulSoup
import html2text
import streamlit as st
from urllib.parse import urljoin, urlparse


def is_valid_url(url, base_url):
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(url)
    return (
        parsed_url.netloc == parsed_base.netloc or not parsed_url.netloc
    ) and not parsed_url.path.endswith((".jpg", ".png", ".gif", ".css", ".js"))


def fetch_html_pages(base_url, visited=None):
    if visited is None:
        visited = set()

    try:
        response = requests.get(base_url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")

        visited.add(base_url)
        links = soup.find_all("a", href=True)

        html_links = set()
        for link in links:
            full_url = urljoin(base_url, link["href"])
            if is_valid_url(full_url, base_url) and full_url not in visited:
                html_links.add(full_url)

        return html_links
    except requests.RequestException as e:
        st.error(f"Error fetching page {base_url}: {e}")
        return set()


def save_markdown_file(url, output_dir):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")

        converter = html2text.HTML2Text()
        converter.ignore_links = False

        main_content = soup.find("main")
        if main_content:
            markdown = converter.handle(str(main_content))
        else:
            markdown = converter.handle(str(soup))

        parsed_url = urlparse(url)
        file_name = parsed_url.path.strip("/").replace("/", "_") or "index"
        file_name = file_name + ".md"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(markdown)

        return file_name
    except requests.RequestException as e:
        st.error(f"Error fetching or saving {url}: {e}")
    except IOError as e:
        st.error(f"Error writing to file for {url}: {e}")
    return None


if __name__ == "__main__":
    st.title("aider.chat Website Scraper")
    base_url = st.text_input("Base URL", "https://aider.chat")
    output_dir = st.text_input("Output Directory", "aider_chat_content")
    scrape_button = st.button("Start Scraping")

    if scrape_button:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with st.spinner("Fetching HTML pages..."):
            all_urls = fetch_html_pages(base_url)

        if all_urls:
            st.write(f"Found {len(all_urls)} HTML pages to scrape.")

            progress_bar = st.progress(0)
            status_text = st.empty()
            saved_files = []

            for i, url in enumerate(all_urls):
                status_text.text(f"Scraping page {i+1} of {len(all_urls)}")
                file_name = save_markdown_file(url, output_dir)
                if file_name:
                    saved_files.append(file_name)
                progress_bar.progress((i + 1) / len(all_urls))

            status_text.text("Scraping completed!")
            st.success(
                f"Saved {len(saved_files)} Markdown files in the `{output_dir}` directory."
            )
            if saved_files:
                st.write("Saved files:")
                for file in saved_files:
                    st.write(f"- {file}")
        else:
            st.warning("No HTML pages found. Please check the base URL and try again.")
