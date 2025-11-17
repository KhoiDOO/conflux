import os
from typing import List
from .core import CVFCrawler
from datetime import datetime


class CvF_Crawler_Interface(CVFCrawler):
    def __init__(self) -> None:
        super().__init__()
        
        self.main_url = "https://openaccess.thecvf.com/{}"
        
    def __call__(self, save_dir: str = None, conf: str | list = 'cvpr', year: str = "2023") -> None:
        if conf == "*":
            self.conf_lst = ['CVPR', 'ICCV']
        elif isinstance(conf, list):
            self.conf_lst = [str.upper(c) for c in conf]
        elif isinstance(conf, str):
            self.conf_lst = [str.upper(conf)]
        else:
            raise ValueError("conf should be a conference name or list of conference name")
            
        if year == "*":
            self.years = [str(x) for x in range(2013, datetime.now().year + 1)]
        elif isinstance(year, list):
            self.years = year
        elif isinstance(year, str):
            self.years = [year]
        else:
            raise ValueError("year should be a conference year or list of conference year")
        
        if save_dir is None:
            raise ValueError("save_dir cannot be None")
        elif not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        for _conf in self.conf_lst:
            for _year in self.years:
                conf_name = f"{_conf}{_year}"
                
                conf_url = self.main_url.format(conf_name)
                
                html_text = self.download_url(conf_url)
                
                if html_text is None:
                    continue
                
                print(f"Crawling {conf_name} from {conf_url}")

                if _conf in ['CVPR', 'ICCV']:
                    self.cvpr_iccv_util(conf_url=conf_url, save_dir=save_dir, conf_name=conf_name)
                elif _conf in ['WACV']:
                    self.wacv_util(conf_url=conf_url, save_dir=save_dir, conf_name=conf_name)

    def wacv_util(self, conf_url, save_dir, conf_name):
        all_paper_url = conf_url

        text = self.download_url(all_paper_url)

        self.cvf_util(text=text, save_dir=save_dir, conf_name=conf_name)

    
    def cvpr_iccv_util(self, conf_url, save_dir, conf_name):
        all_paper_url = conf_url + "?day=all"
                
        all_day_text = self.download_url(all_paper_url)

        self.cvf_util(text=all_day_text, save_dir=save_dir, conf_name=conf_name)
    
    def cvf_util(self, text, save_dir, conf_name):
        
        html_parser = self.get_parser(html=text)
        
        hrefs = [x.find_all('a', href=True) for x in html_parser.find_all("dd")]
        hrefs = [x for x in hrefs if len(x) > 0]
        main_paper_urls = []
        sup_paper_urls = []

        for urls in hrefs:
            main_paper_urls.append(urls[0]['href'][1:])
            if len(urls) > 1:
                sup_paper_urls.append(urls[1]['href'][1:])
            else:
                sup_paper_urls.append(None)

        main_paper_pdf_urls = [self.main_url.format(x) for x in main_paper_urls if 'pdf' in x]
        sup_paper_pdf_urls = [self.main_url.format(x) for x in sup_paper_urls if x is not None and 'pdf' in x]

        num_main_papers = len(main_paper_pdf_urls)
        num_sup_papers = len([x for x in sup_paper_pdf_urls if x is not None])

        print(f"Found {num_main_papers} papers and {num_sup_papers} supplementary materials in {conf_name}")
        # print("Sample main paper URL:", main_paper_pdf_urls[0])
        # print("Sample supplementary material URL:", sup_paper_pdf_urls[0] if sup_paper_pdf_urls[0] is not None else "N/A")
        print("Start downloading...")

        for name, urls in zip(["main", "supplementary"], [main_paper_pdf_urls, sup_paper_pdf_urls]):
            
            sub_save_dir = save_dir + f"/{conf_name}/{name}"
            os.makedirs(sub_save_dir, exist_ok=True)

            print(f"Downloading {name} papers to {sub_save_dir}...")
            super().__call__(urls=urls, save_dir=sub_save_dir)