import json
import requests
from bs4 import BeautifulSoup

# Function to crawl Jekyll JSON files and update index
def crawl_jekyll_json(url, index_file):
    response = requests.get(url)
    if response.status_code == 200:
        jekyll_data = response.json()
        for page in jekyll_data:
            page_data = {
                'link': page['url'],
                'title': page['title'],
                'description': page.get('description', page.get('snippet', '')),
                # Add other relevant fields
            }
            # Append the page_data to the index.json file
            append_to_index(page_data, index_file)

# Function to crawl XML sitemaps and update index
def crawl_xml_sitemaps(url, index_file):
    response = requests.get(url)
    if response.status_code == 200:
        sitemap_data = response.text
        soup = BeautifulSoup(sitemap_data, 'xml')
        urls = soup.find_all('url')
        for url in urls:
            page_url = url.findNext('loc').text

            # Make a request to the page URL
            page_response = requests.get(page_url)
            if page_response.status_code == 200:
                page_content = page_response.text
                page_soup = BeautifulSoup(page_content, 'html.parser')

                # Extract the title
                title_element = page_soup.find('title')
                page_title = title_element.text if title_element else ''

                # Extract the description
                meta_description = page_soup.find('meta', attrs={'name': 'description'})
                page_description = meta_description['content'] if meta_description else ''

                page_data = {
                    'link': page_url,
                    'title': page_title,
                    'description': page_description,
                    # Add other relevant fields
                }
                # Append the page_data to the index.json file
                append_to_index(page_data, index_file)

# Function to crawl GitHub repository and update index
def crawl_github_repo(url, index_file):
    response = requests.get(url)
    if response.status_code == 200:
        page_data = {
            'link': url,
            'title': '',
            'description': '',
            'pages': []
        }

        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href.startswith('/') and not href.endswith('.git') and url in href and href.count('/') > url.count('/'):
                page_url = 'https://github.com' + href
                page_response = requests.get(page_url)
                if page_response.status_code == 200:
                    page_content = page_response.text
                    page_soup = BeautifulSoup(page_content, 'html.parser')

                    # Extract the title
                    title_element = page_soup.find('title')
                    page_title = title_element.text if title_element else ''

                    page_data['pages'].append({'link': page_url, 'title': page_title})

        # Append the page_data to the index.json file
        append_to_index(page_data, index_file)

# Function to get existing data for a given link from index.json file
def get_data_from_index(link, index_data):
    for data in index_data:
        if data['link'] == link:
            return data
    return None

# Function to merge new data with existing data
def merge_data(existing_data, new_data):
    existing_pages = existing_data.get('pages', [])
    new_pages = new_data.get('pages', [])
    existing_pages.extend(new_pages)
    existing_data['pages'] = existing_pages

# Function to append page_data to index.json file
def append_to_index(page_data, index_file):
    try:
        with open(index_file, 'r') as f:
            index_data = json.load(f)
    except FileNotFoundError:
        index_data = []

    # Check if the link already exists in the index.json file
    existing_data = get_data_from_index(page_data['link'], index_data)
    if existing_data:
        # Merge the new page_data with the existing data
        merge_data(existing_data, page_data)
    else:
        index_data.append(page_data)

    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=4)
    print(f"Added/updated {list(page_data.keys())} in {page_data['link']}")

# Read the list of URLs from a plain text file
def read_url_list(file_path):
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()
    return urls

# Main function
def main():
    # Read the list of Jekyll JSON files
    jekyll_json_urls = read_url_list('../db/json.txt')
    jekyll_json_index_file = '../index/web/v1/index.json'
    # Crawl Jekyll JSON files and update index
    for url in jekyll_json_urls:
        crawl_jekyll_json(url, jekyll_json_index_file)

    # Read the list of XML sitemaps
    xml_sitemap_urls = read_url_list('../db/xml.txt')
    xml_sitemap_index_file = '../index/web/v1/index.json'
    # Crawl XML sitemaps and update index
    for url in xml_sitemap_urls:
        crawl_xml_sitemaps(url, xml_sitemap_index_file)

# Execute the main function
if __name__ == '__main__':
    main()
