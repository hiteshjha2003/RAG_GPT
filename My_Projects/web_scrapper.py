import streamlit as st
import requests
from bs4 import BeautifulSoup

def fetch_and_parse(url):
    response = requests.get(url)
    if response.status_code == 200:
        page_content = response.content
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup
    else:
        st.error(f"Failed to retrieve content. Status code: {response.status_code}")
        return None

def display_content(soup):
    if soup:
        # Display all text content
        st.subheader("Text Content")
        for paragraph in soup.find_all('p'):
            st.write(paragraph.get_text())

        # Display all hyperlinks
        st.subheader("Hyperlinks")
        for link in soup.find_all('a', href=True):
            st.write(f"[{link.get_text()}]({link['href']})")

        # Display all images
        st.subheader("Images")
        for image in soup.find_all('img'):
            img_url = image.get('src')
            if img_url:
                st.image(img_url)

def main():
    st.title("Web Scraping Application")
    url = st.text_input("Enter the URL of the webpage you want to scrape:")

    if st.button("Scrape"):
        if url:
            soup = fetch_and_parse(url)
            display_content(soup)
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
