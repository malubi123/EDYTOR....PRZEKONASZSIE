import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Ścieżka do lokalnych plików
LOCAL_DIR = 'local_site'

def save_resource(url, base_url, folder):
    """Pobiera i zapisuje zasób ze strony."""
    try:
        resource_url = urljoin(base_url, url)
        parsed_url = urlparse(resource_url)
        resource_path = os.path.join(folder, parsed_url.path.lstrip('/'))
        
        if not os.path.splitext(resource_path)[1]:
            resource_path = os.path.join(resource_path, 'index.html')
        
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)
        
        response = requests.get(resource_url)
        if response.status_code == 200:
            with open(resource_path, 'wb') as file:
                file.write(response.content)
            return parsed_url.path
        else:
            print(f"Nie udało się pobrać {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Nie udało się pobrać {url}: {e}")
        return None

def download_all_resources(url):
    """Pobiera stronę i jej zasoby, zapisuje lokalnie."""
    if os.path.exists(LOCAL_DIR):
        for root, dirs, files in os.walk(LOCAL_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    else:
        os.makedirs(LOCAL_DIR, exist_ok=True)
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = url
        
        # Pobierz wszystkie skrypty, arkusze stylów i inne zasoby
        for tag in soup.find_all(['script', 'link', 'img']):
            if tag.name == 'script' and tag.get('src'):
                src = tag['src']
                tag['src'] = save_resource(src, base_url, LOCAL_DIR)
            elif tag.name == 'link' and tag.get('href') and 'stylesheet' in tag.get('rel', []):
                href = tag['href']
                tag['href'] = save_resource(href, base_url, LOCAL_DIR)
            elif tag.name == 'img' and tag.get('src'):
                src = tag['src']
                tag['src'] = save_resource(src, base_url, LOCAL_DIR)

        # Zapisz zaktualizowany HTML
        with open(os.path.join(LOCAL_DIR, 'index.html'), 'w', encoding='utf-8') as file:
            file.write(str(soup))
        
        print(f"Strona oraz wszystkie zasoby zostały pobrane i zapisane w folderze '{LOCAL_DIR}'")
    else:
        print(f"Błąd podczas pobierania strony: {response.status_code}")

if __name__ == "__main__":
    url = input("Podaj adres URL strony do pobrania: ")
    download_all_resources(url)
