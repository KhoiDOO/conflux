import os, sys
from typing import List
import requests

from bs4 import BeautifulSoup
from alive_progress import alive_it

class CVFCrawler:
    def __init__(self) -> None:
        pass

    def __call__(self, urls: List | str = None, save_dir: str = None) -> None:
        if urls == "*":
            raise NotImplementedError("Crawling all papers is under implementation")

        elif urls is None:
            raise ValueError("urls cannot be None")
        
        if save_dir is None:
            raise ValueError("save_dir cannot be None")
    
        for url in alive_it(urls, title="Cloning Papers..."):
            
            filename = url.split("/")[-1]
            print(f"Cloning: {filename}")
            
            savepath = save_dir + f"/{filename}"
            if os.path.exists(savepath):
                continue
            
            source = requests.get(url)
            
            with open(savepath, 'wb') as f:
                f.write(source.content)
        
    def download_url(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None 

    def get_parser(self, html: str):
        return BeautifulSoup(html, 'html.parser')