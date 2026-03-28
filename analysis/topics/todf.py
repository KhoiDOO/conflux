import os
import argparse
import json

from glob import glob
from alive_progress import alive_it

import polars as pl


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert topic JSON files to a DataFrame and save as Parquet.")
    parser.add_argument("--topics_dir", type=str, required=True, help="Directory containing topic JSON files.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output Parquet file.")
    
    args = parser.parse_args()
    topics_dir = args.topics_dir
    output_path = args.output_path

    json_files = glob(os.path.join(topics_dir, "*.json"))
    all_data = []

    for json_file in alive_it(json_files, title="Processing topic JSON files"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            paper_id = os.path.basename(json_file).replace('.json', '')
            data['paper_id'] = paper_id
            all_data.append(data)

    df = pl.DataFrame(all_data)
    df.write_parquet(output_path)
    print(f"Saved topics DataFrame to {output_path}.")