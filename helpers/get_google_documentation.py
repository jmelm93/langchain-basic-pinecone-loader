import os
import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup

# Constants
XPATH_EXPRESSION = "//div[contains(@class,'devsite-article-body')]"  # XPath expression to extract content
PATH_TO_URL_CONTEXT = "data/urls.csv" # Path to the CSV file with 'Page Name' and 'URL'
HTML_FOLDER = 'html'  # Folder containing HTML files
TXT_FOLDER = 'txt'    # Folder to store text files

# Function to clean page names for file names
def clean_page_names(page_name):
    return page_name.lower().replace('-', '_').replace(' ', '-').replace('&', '').replace('--', '-').replace('-_-', '_')


# Function to extract HTML and save to file
def extract_and_save_html(row):
    page_name = row['Page Name']
    url = row['URL']
    response = requests.get(url)
    
    if response.status_code == 200:
        # Create the data folder if it doesn't exist
        if not os.path.exists(HTML_FOLDER):
            os.makedirs(HTML_FOLDER)
        
        # Parse the HTML content
        tree = html.fromstring(response.text)
        article_element = tree.xpath(XPATH_EXPRESSION)
        
        if article_element:
            # Get the first matching element
            article_element = article_element[0]
            
            # Save the HTML content to a file
            file_path = os.path.join(HTML_FOLDER, f'{clean_page_names(page_name)}.html')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html.tostring(article_element, pretty_print=True, encoding='unicode'))
            print(f'Saved HTML for {page_name} to {file_path}')
        else:
            print(f'No matching element found for {page_name}')
    else:
        print(f'Failed to fetch URL for {page_name}: Status code {response.status_code}')


# Function to extract HTML and convert to text. No storage.
def extract_and_convert_html_to_text(row):
    page_name = row['Page Name']
    url = row['URL']
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the HTML content
        tree = html.fromstring(response.text)
        article_element = tree.xpath(XPATH_EXPRESSION)
        
        if article_element:
            # Get the first matching element
            article_element = article_element[0]
            
            # Convert the HtmlElement to a string
            article_html = html.tostring(article_element, pretty_print=True, encoding='unicode')
            
            # Get BeautifulSoup object from the HTML string
            soup = BeautifulSoup(article_html, 'html.parser')
            
            # Convert to text
            text = soup.get_text(separator='\n', strip=True)
            return text
        else:
            print(f'No matching element found for {page_name}')
    else:
        print(f'Failed to fetch URL for {page_name}: Status code {response.status_code}')


# Function to convert HTML to text and save to a .txt file
def html_to_text_and_save(html_file):
    # Create the TXT folder if it doesn't exist
    if not os.path.exists(TXT_FOLDER):
        os.makedirs(TXT_FOLDER)
    
    file_name = os.path.basename(html_file)
    txt_file_path = os.path.join(TXT_FOLDER, f'{os.path.splitext(file_name)[0]}.txt')
    
    with open(html_file, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    
    print(f'Saved text from {file_name} to {txt_file_path}')


# job to create html files from urls
def create_html_files():
    # Read the DataFrame with 'Page Name' and 'URL'
    data = pd.read_csv(PATH_TO_URL_CONTEXT) 

    # Apply the extraction function to each row
    data.apply(extract_and_save_html, axis=1)


# job to create txt files from html files
def create_txt_files():
    # List all HTML files in the HTML folder
    html_files = [os.path.join(HTML_FOLDER, file) for file in os.listdir(HTML_FOLDER) if file.endswith('.html')]

    # Convert and save HTML files to text files
    for html_file in html_files:
        html_to_text_and_save(html_file)


if __name__ == '__main__':
    # create_html_files()
    create_txt_files()
