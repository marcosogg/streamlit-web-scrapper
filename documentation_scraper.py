import os
import requests
from bs4 import BeautifulSoup
import html2text
import streamlit as st


def fetch_documentation_pages(base_url):
    index_page = requests.get(base_url)
    soup = BeautifulSoup(index_page.content, "html.parser")
    links = soup.find_all("a", href=True)
    doc_links = [link["href"] for link in links if link["href"].startswith("/docs/")]
    return list(set(doc_links))  # Remove duplicates


def save_markdown_files(doc_links, base_url, output_dir, file_name):
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    page = requests.get(base_url + doc_links[0])  # Assuming only one documentation page for simplicity
    soup = BeautifulSoup(page.content, "html.parser")
    markdown = converter.handle(str(soup))
    file_name_with_extension = file_name + ".md"
    with open(os.path.join(output_dir, file_name_with_extension), "w") as file:
        file.write(markdown)


if __name__ == "__main__":
    st.title("Documentation Scraper")
    base_url = st.text_input("Base URL", "https://aider.chat")
    output_dir = st.text_input("Output Directory", "documentation")
    file_name = st.text_input("File Name", "documentation_page")
    scrape_button = st.button("Start Scraping")

    if scrape_button:
        with st.spinner("Fetching documentation pages..."):
            doc_links = fetch_documentation_pages(base_url + "/docs/")
        with st.spinner("Saving Markdown files..."):
            save_markdown_files(doc_links, base_url, output_dir, file_name)
        st.success("Scraping completed!")
        st.write(f"Markdown file `{file_name_with_extension}` is saved in the `{output_dir}` directory.")
