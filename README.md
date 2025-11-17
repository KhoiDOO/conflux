Conflux — Crawling research papers and converting PDFs

# Updates
- v0.0.5 (17th Nov 2025): Added `PaperDoclingParser` wrapper, exported key classes at package top-level, and improved example scripts.
- v0.0.1 (29th Dec 2024): CVPR, ICCV conference papers crawling (by year or conference)

# Installation
First clone the repository and install in editable mode:

```bash
git clone https://github.com/KhoiDOO/conflux.git
cd conflux
pip install -e .
```

The package exposes `CVFCrawler`, `PaperDoclingParser`, and `CvF_Crawler_Interface` from the `conflux` top-level module.

# Usage

## Crawling a list of paper links
Use `CVFCrawler` to download a list of PDF links to a directory:

```python
import os
from conflux import CVFCrawler

if __name__ == "__main__":
    links = [
        "https://openaccess.thecvf.com/content/CVPR2023/html/Chen_Transfer_Knowledge_From_Head_to_Tail_Uncertainty_Calibration_Under_Long-Tailed_CVPR_2023_paper.html",
        # add more paper PDF URLs
    ]

    crawler = CVFCrawler()

    save_dir = os.path.join(os.getcwd(), "cvpr_2023")
    os.makedirs(save_dir, exist_ok=True)

    crawler(urls=links, save_dir=save_dir)
```

## Crawling all papers from conferences (CVPR / ICCV / WACV)
Use `CvF_Crawler_Interface` to crawl by conference and year. Pass `conf='*'` and/or `year='*'` to select all.

```python
import os
from conflux import CvF_Crawler_Interface

if __name__ == "__main__":
    iface = CvF_Crawler_Interface()

    iface(
        save_dir=os.path.join(os.getcwd(), "clone"),
        conf='cvpr',   # 'cvpr', 'iccv', ['cvpr','iccv'], or '*' for all supported
        year='2023'    # single year, list of years, or '*' for all years since 2013
    )
```

## Parsing PDFs into structured outputs
`PaperDoclingParser` wraps the `docling` document converter to export JSON, Markdown, HTML or doctags from a PDF.

```python
from conflux import PaperDoclingParser

parser = PaperDoclingParser()

# parse and get outputs as dict/markdown/html/doctags
outputs = parser.get_parse("/path/to/paper.pdf", return_dict=True, return_markdown=True)

# or parse and save outputs to files
parser(
    file_path="/path/to/paper.pdf",
    save_dir="/path/to/output",
    return_dict=True,
    return_markdown=True,
)
```

# Notes
- The repository depends on `docling`, `requests`, `beautifulsoup4`, and `alive-progress`. See `requirements.txt` for the full list.
- `CVFCrawler` currently raises `NotImplementedError` when called with `urls="*"` (bulk crawling from all conferences is handled by `CvF_Crawler_Interface`).

If you'd like, I can also update the examples in `example/` to match these names or add a short quickstart script.
