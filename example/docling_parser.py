import argparse
import os

from conflux import PaperDoclingParser
from alive_progress import alive_it
from glob import glob

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Docling XML files for CVF papers")
    parser.add_argument("--save_dir", type=str, default=os.getcwd() + "/clone", help="Directory to save papers")
    parser.add_argument("--conf", type=str, default="cvpr", help="Conference name")
    parser.add_argument("--year", type=str, nargs='+', default=["2025"], help="Conference year(s)")
    
    args = parser.parse_args()

    docling_parser = PaperDoclingParser()

    conf_name = args.conf.upper()
    
    for year in args.year:
        conf_dir = os.path.join(args.save_dir, f"{conf_name}{year}")
        if not os.path.exists(conf_dir):
            print(f"Directory {conf_dir} does not exist. Skipping...")
            continue

        print(f"Parsing papers in {conf_dir}...")
        
        main_paper_dir = os.path.join(conf_dir, "main")
        sup_paper_dir = os.path.join(conf_dir, "supplementary")

        docling_main_dir = os.path.join(conf_dir, "docling_main")
        docling_sup_dir = os.path.join(conf_dir, "docling_sup")

        main_pdfs = glob(os.path.join(main_paper_dir, "*.pdf"))
        sup_pdfs = glob(os.path.join(sup_paper_dir, "*.pdf"))

        print(f"Parsing main papers...")
        for pdf_path in alive_it(main_pdfs):
            try:
                docling_parser(
                    file_path=pdf_path,
                    save_dir=docling_main_dir,
                    return_dict=True,
                    return_markdown=True,
                    return_html=True,
                    return_doctags=True,
                )
            except Exception as e:
                print(f"Error parsing {pdf_path}: {e}")
        
        print(f"Parsing supplementary papers...")
        for pdf_path in alive_it(sup_pdfs):
            try:
                docling_parser(
                    file_path=pdf_path,
                    save_dir=docling_sup_dir,
                    return_dict=True,
                    return_markdown=True,
                    return_html=True,
                    return_doctags=True,
                )
            except Exception as e:
                print(f"Error parsing {pdf_path}: {e}")