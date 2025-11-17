import os, sys
import argparse

from conflux import CvF_Crawler_Interface


if __name__ == "__main__":
    
    cvf_interface = CvF_Crawler_Interface()
    
    parser = argparse.ArgumentParser(description="Crawl CVF papers")
    parser.add_argument("--save_dir", type=str, default=os.getcwd() + "/clone", help="Directory to save papers")
    parser.add_argument("--conf", type=str, default="cvpr", help="Conference name")
    parser.add_argument("--year", type=str, nargs='+', default=["2025"], help="Conference year(s)")
    
    args = parser.parse_args()
    
    cvf_interface(
        save_dir=args.save_dir,
        conf=args.conf,
        year=args.year
    )