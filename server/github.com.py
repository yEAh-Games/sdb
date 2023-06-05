import json
import requests
from bs4 import BeautifulSoup

# Function to crawl GitHub repository and update index
def crawl_github_repo(url, index_data, github_index_file):
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

        # Append the page_data to the index_data list
        index_data.append(page_data)

        # Output the GitHub index objects to a separate JSON file
        output_github_index(page_data, github_index_file)

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

# Function to output GitHub index objects to a separate JSON file
def output_github_index(page_data, output_file):
    github_index_data = page_data['pages']
    with open(output_file, 'w') as f:
        json.dump(github_index_data, f, indent=4)
    for page in github_index_data:
        print(f"Added/updated ['link', 'title'] in {page['link']}")

# Function to get existing data for a given link from index.json file
def get_data_from_index(link, index_data):
    for data in index_data:
        if data['link'] == link:
            return data
    return None

# Read the list of URLs from a plain text file
def read_url_list(file_path):
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()
    return urls

# Main function
def main():
    # Read the list of GitHub repository URLs
    github_repo_urls = read_url_list('../db/github.txt')
    github_index_file = '../index/web/v1/github.com.json'

    # Initialize an empty index_data list
    index_data = []

    # Crawl GitHub repositories and update index
    for url in github_repo_urls:
        crawl_github_repo(url, index_data, github_index_file)

    # Write the index_data to the index.json file
    with open(github_index_file, 'w') as f:
        json.dump(index_data, f, indent=4)

    print(f"Added/updated {len(index_data)} GitHub index objects to {github_index_file}")

# Execute the main function
if __name__ == '__main__':
    main()
