import os
import requests
import json

from typing import List
from .constants import *

from bs4 import BeautifulSoup
from alive_progress import alive_it

from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionResult
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode


class CVFCrawler:
    def __init__(
        self
    ) -> None:
        pass

    def __call__(
        self, 
        urls: List | str = CVFCRAWLER_URLS, 
        save_dir: str = CVFCRAWLER_SAVEDIR
    ) -> None:
        if urls == "*":
            raise NotImplementedError("Crawling all papers is under implementation")

        elif urls is None:
            raise ValueError("urls cannot be None")
        
        if save_dir is None:
            raise ValueError("save_dir cannot be None")
    
        for url in alive_it(urls, title=CVFCRAWLER_ALIVE_PROGRESS_TITLE):
            
            filename = url.split("/")[-1]
            
            savepath = save_dir + f"/{filename}"
            if os.path.exists(savepath):
                continue
            
            source = requests.get(url)
            
            with open(savepath, 'wb') as f:
                f.write(source.content)
        
    def download_url(
        self, 
        url: str
    ):
        response = requests.get(url)
        if response.status_code == CVFCRAWLER_SUCCESS_STATUS_CODE:
            return response.text
        else:
            return None 

    def get_parser(
        self, 
        html: str
    ):
        return BeautifulSoup(html, CVFCRAWLER_PARSER)


class PaperDoclingParser:
    def __init__(
        self,
        pdf_pipeline_options: dict = {
            "do_table_structure": PDP_DO_TABLE_STRUCTURE,
            "do_picture_classification": PDP_DO_PICTURE_CLASSIFICATION,
            "do_picture_description": PDP_DO_PICTURE_DESCRIPTION,
        },
    ) -> None:
        self.pipeline_options = PdfPipelineOptions(**pdf_pipeline_options)
        self.pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=self.pipeline_options)
            }
        )
    
    def get_parse(
        self, 
        file_path: str,
        return_dict: bool = PDP_RETURN_DICT,
        return_markdown: bool = PDP_RETURN_MARKDOWN,
        return_html: bool = PDP_RETURN_HTML,
        return_doctags: bool = PDP_RETURN_DOCTAGS,
    ):
        
        result: ConversionResult = self.converter.convert(file_path)

        outputs = {}

        if return_dict:
            dict_result = result.document.export_to_dict()
            outputs[PDP_OUTPUT_DICT_KEY] = dict_result
        
        if return_markdown:
            markdown_output = result.document.export_to_markdown(
                image_placeholder=''
            )
            outputs[PDP_OUTPUT_MD_KEY] = markdown_output
        
        if return_html:
            html_output = result.document.export_to_html()
            outputs[PDP_OUTPUT_HTML_KEY] = html_output
        
        if return_doctags:
            doctags_output = result.document.export_to_doctags()
            outputs[PDP_OUTPUT_DOCTAGS_KEY] = doctags_output
        return outputs
    
    def save_parse(
        self, 
        file_path: str,
        return_dict: bool = PDP_RETURN_DICT,
        return_markdown: bool = PDP_RETURN_MARKDOWN,
        return_html: bool = PDP_RETURN_HTML,
        return_doctags: bool = PDP_RETURN_DOCTAGS,
        dict_save_path: str = PDP_DICT_SAVE_PATH,
        markdown_save_path: str = PDP_MD_SAVE_PATH,
        html_save_path: str = PDP_HTML_SAVE_PATH,
        doctags_save_path: str = PDP_DOCTAGS_SAVE_PATH,
    ):
        assert return_dict or return_markdown or return_html or return_doctags, \
            "At least one return format must be True."
    
        assert (dict_save_path is None) or return_dict, \
            "dict_save_path is provided but return_dict is False."
        
        assert (markdown_save_path is None) or return_markdown, \
            "markdown_save_path is provided but return_markdown is False."
        
        assert (html_save_path is None) or return_html, \
            "html_save_path is provided but return_html is False."
        
        assert (doctags_save_path is None) or return_doctags, \
            "doctags_save_path is provided but return_doctags is False."
        
        assert os.path.exists(file_path), \
            f"File {file_path} does not exist."
    
        assert (dict_save_path.endswith('.json') if dict_save_path is not None else True), \
            "dict_save_path must end with .json"
    
        assert (markdown_save_path.endswith('.md') if markdown_save_path is not None else True), \
            "markdown_save_path must end with .md"
        
        assert (html_save_path.endswith('.html') if html_save_path is not None else True), \
            "html_save_path must end with .html"
        
        assert (doctags_save_path.endswith('.txt') if doctags_save_path is not None else True), \
            "doctags_save_path must end with .txt"
        
        outputs = self.get_parse(
            file_path=file_path,
            return_dict=return_dict,
            return_markdown=return_markdown,
            return_html=return_html,
            return_doctags=return_doctags,
        )

        if dict_save_path is not None:
            if not os.path.exists(dict_save_path):
                with open(dict_save_path, 'w') as f:
                    json.dump(outputs['dict'], f, indent=4)
        
        if markdown_save_path is not None:
            if not os.path.exists(markdown_save_path):
                with open(markdown_save_path, 'w') as f:
                    f.write(outputs['markdown'])
        
        if html_save_path is not None:
            if not os.path.exists(html_save_path):
                with open(html_save_path, 'w') as f:
                    f.write(outputs['html'])
        
        if doctags_save_path is not None:
            if not os.path.exists(doctags_save_path):
                with open(doctags_save_path, 'w') as f:
                    f.write(outputs['doctags'])
    
    def __call__(
        self,
        file_path: str,
        save_dir: str = PDP_SAVE_DIR,
        return_dict: bool = PDP_RETURN_DICT,
        return_markdown: bool = PDP_RETURN_MARKDOWN,
        return_html: bool = PDP_RETURN_HTML,
        return_doctags: bool = PDP_RETURN_DOCTAGS,
        max_file_size_mb: int = PDP_PDF_MAX_FILE_SIZE_MB,
    ):
        
        if os.path.getsize(file_path) > max_file_size_mb * 1024 * 1024:
            print(f"File {file_path} exceeds the maximum size of {max_file_size_mb} MB. Skipping...")
            return
        
        save_dir = os.path.dirname(file_path) if save_dir is None else save_dir
        os.makedirs(save_dir, exist_ok=True)
        dict_save_path = os.path.join(save_dir, os.path.basename(file_path).replace('.pdf', '.json')) if return_dict else None
        markdown_save_path = os.path.join(save_dir, os.path.basename(file_path).replace('.pdf', '.md')) if return_markdown else None
        html_save_path = os.path.join(save_dir, os.path.basename(file_path).replace('.pdf', '.html')) if return_html else None
        doctags_save_path = os.path.join(save_dir, os.path.basename(file_path).replace('.pdf', '.txt')) if return_doctags else None

        if all(os.path.exists(path) for path in [dict_save_path, markdown_save_path, html_save_path, doctags_save_path] if path is not None):
            return

        self.save_parse(
            file_path=file_path,
            return_dict=return_dict,
            return_markdown=return_markdown,
            return_html=return_html,
            return_doctags=return_doctags,
            dict_save_path=dict_save_path,
            markdown_save_path=markdown_save_path,
            html_save_path=html_save_path,
            doctags_save_path=doctags_save_path,
        )