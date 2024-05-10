import os, sys
import requests
from bs4 import BeautifulSoup
import markdownify
import unidecode
from urllib.parse import unquote

ks_dir = 'knowledge_sources/exemplo/'

base_url = "https://exemplo.com.br"

path_url = "/html-para-markdown/python/"

first_url = "pagina1/"

base_doc_url = base_url + path_url + first_url

all_url = []


def cleanup(url):
    try:
        return unquote(url, errors='strict')
    except UnicodeDecodeError:
        return unquote(url, encoding='latin-1')


def remove_div_child_element(body, div_class):
    unused = body.find('div', class_=div_class)
    unused.clear()


def get_sub_url(body):
    try:
        # find all the anchor tags with "href"
        urlList = []
        if body is not None:
            for link in body.find_all('a'):
                urlList.append(link.get('href'))
            urlList=repair_sub_url(urlList)
        return urlList
    except Exception as e:
        #print(f"Failed to scrape {url}: {e}")
        sys.exit(f"Failed to get_sub_url body: {body}: {e}")


def repair_sub_url(urlList):
	newList = []
	for url in urlList:
		newList.append(base_url + url if url.startswith(path_url + first_url) else url)
	newList=remove_invalid_url(newList)
	return newList

		
def remove_invalid_url(urlList):
	newList = [url for i, url in enumerate(urlList) 
            if url.startswith(base_doc_url) 
            and "#" not in url 
            and ".zip"]
     
	return newList


def convert_html_to_markdown(html):
    markdown = markdownify.markdownify(html, heading_style="ATX", strip=["pre"])
    print(markdown)
    return markdown


def get_file_name_from_url(url):
    for word in url.split("/"):
         print(word)
    file_name = unidecode.unidecode(cleanup(url)).replace(base_url + path_url, "").replace('/', '_')
    file_name = file_name.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~=+"})
    return file_name + '.md'


def save_markdown_file(markdown, file_name):
    f = open(ks_dir + file_name, 'w')
    f.write(markdown)
    f.close


def get_page(url):
    try:

        # Making a GET request
        r = requests.get(url)
        
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'html.parser')

        # Getting the main content of page by div
        body = soup.find('div', class_="td-content")

        remove_div_child_element(body, "d-print-none")
        #print(body)
        
        file_name = get_file_name_from_url(url)
        print(file_name)
        
        markdown = convert_html_to_markdown(body.prettify())

        save_markdown_file(markdown, file_name)

        print(f"Successfully created {file_name}")
      
    except Exception as e:
        #print(f"Failed to scrape {url}: {e}")
        sys.exit(f"Failed to get_page {url}: {e}")


def get_all_url(url):
    try:
    
        # Making a GET request
        try:
            r = requests.get(url)
            if r.status_code == 404:
                print(f"404 : {url}")
                return
        except Exception as e:
            raise SystemExit(f"Failed to GET {url}: {e}")
        
        # Parsing the HTML code
        soup = BeautifulSoup(r.content, 'html.parser')

        if soup is None:
            return

        # Getting the main content of page by div
        body = soup.find('div', class_="td-content")

        if body is None:
            return
        
        if url not in all_url:
            print(f"Adding URL : {url}")
            all_url.append(url)
        else:
            return
        
        urlList = get_sub_url(body)
        for subUrl in urlList:
            print(f"     SUB URL : {subUrl}")
        
        print("\n")
           
        for subUrl in urlList:
            get_all_url(subUrl)

 
    except Exception as e:
        print(f"Failed to get_all_url {url}: {e}")


# Ensure the knowledge_sources directory exists
os.makedirs(ks_dir, exist_ok=True)

get_all_url(base_doc_url)
#print("\n\n\n\n\n\n")

for url in all_url:
    get_page(url)
    print(f"URL FINAL: {url}")






