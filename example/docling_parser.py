import argparse
import os

from conflux import PaperDoclingParser
from alive_progress import alive_it
from glob import glob
import tracemalloc
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Docling XML files for CVF papers")
    parser.add_argument("--save_dir", type=str, default=os.getcwd() + "/clone", help="Directory to save papers")
    parser.add_argument("--conf", type=str, default="cvpr", help="Conference name")
    parser.add_argument("--year", type=str, nargs='+', default=["2025"], help="Conference year(s)")
    parser.add_argument("--parse_sub", action="store_true", help="Also parse supplementary materials")
    parser.add_argument("--debug_mem", action="store_true", help="Enable memory tracing output")
    parser.add_argument("--recreate_parser", action="store_true", help="Recreate PaperDoclingParser for each file (diagnostic)")
    
    args = parser.parse_args()

    # create one parser by default; can be recreated per-file with --recreate_parser
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
                if args.recreate_parser:
                    # recreate parser to see if converter reuse is causing memory growth
                    docling_parser = PaperDoclingParser()

                if args.debug_mem:
                    tracemalloc.start()
                    snap1 = tracemalloc.take_snapshot()
                    t1 = time.time()

                docling_parser(
                    file_path=pdf_path,
                    save_dir=docling_main_dir,
                    return_dict=True,
                    return_markdown=True,
                    return_html=True,
                    return_doctags=True,
                )

                if args.debug_mem:
                    t2 = time.time()
                    snap2 = tracemalloc.take_snapshot()
                    top_stats = snap2.compare_to(snap1, 'lineno')
                    total = sum(stat.size_diff for stat in top_stats)
                    print(f"Parsed {os.path.basename(pdf_path)} in {t2-t1:.2f}s, memory diff: {total/1024:.1f} KiB")
                    # show top few
                    for stat in top_stats[:5]:
                        print(stat)
                    tracemalloc.stop()

            except Exception as e:
                print(f"Error parsing {pdf_path}: {e}")
        
        if args.parse_sub:
            print(f"Parsing supplementary papers...")
            for pdf_path in alive_it(sup_pdfs):
                try:
                    if args.recreate_parser:
                        docling_parser = PaperDoclingParser()

                    if args.debug_mem:
                        tracemalloc.start()
                        snap1 = tracemalloc.take_snapshot()
                        t1 = time.time()

                    docling_parser(
                        file_path=pdf_path,
                        save_dir=docling_sup_dir,
                        return_dict=True,
                        return_markdown=True,
                        return_html=True,
                        return_doctags=True,
                    )

                    if args.debug_mem:
                        t2 = time.time()
                        snap2 = tracemalloc.take_snapshot()
                        top_stats = snap2.compare_to(snap1, 'lineno')
                        total = sum(stat.size_diff for stat in top_stats)
                        print(f"Parsed {os.path.basename(pdf_path)} in {t2-t1:.2f}s, memory diff: {total/1024:.1f} KiB")
                        for stat in top_stats[:5]:
                            print(stat)
                        tracemalloc.stop()

                except Exception as e:
                    print(f"Error parsing {pdf_path}: {e}")