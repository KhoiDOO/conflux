import os, sys

from cvf_crawler import CvF_Crawler_Interface


if __name__ == "__main__":
    
    cvf_interface = CvF_Crawler_Interface()
    
    cvf_interface(
        save_dir=os.getcwd() + "/clone",
        conf='cvpr',
        year="2023"
    )