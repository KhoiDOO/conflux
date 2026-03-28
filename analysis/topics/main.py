import os
import argparse
import json
import outlines

from transformers import AutoModelForCausalLM, AutoTokenizer

from pydantic import BaseModel, Field
from enum import Enum
from guidance import json as gen_json
from guidance.models import Transformers
from guidance import system, user, assistant, gen

from glob import glob
from alive_progress import alive_it
import warnings

warnings.filterwarnings(
    "ignore",
    message=r"Cache is too small.*",
    category=UserWarning,
)

MODEL = 'meta-llama/Llama-3.2-3B-Instruct'
VERBOSE = False

SYSTEM_PROMPT = """
You are a scientific research assistant. Analyze whether a given abstract is related to 3D research.

"3D research" includes:
- 3D Computer Vision (Stereo, Depth, Point Clouds, Reconstruction, NeRF)
- 3D Graphics (Rendering, Meshes, Voxels)
- 3D Printing / Additive Manufacturing
- VR/AR (Spatial computing)
- Volumetric medical imaging (CT/MRI segmentation)
- More generally, any research that fundamentally involves three-dimensional data or environments.
"""

USER_PROMPT = """
Abstract:
"{0}"

Return a JSON object with exactly these keys:
- "is_3d": boolean (true if related, false if not)
- "is_generative": boolean (true if generative research, false otherwise)
- "topic": string (short categorization, e.g., "NLP", "3D Reconstruction", "VR")
- "reason": string (1 sentence explanation)
"""

class TopicExtractionResult(BaseModel):
    is_3d: bool = Field(description="True if related to 3D research, false otherwise")
    is_generative: bool = Field(description="True if generative research, false otherwise")
    topic: str = Field(description="Short categorization, e.g., 'NLP', '3D Reconstruction', 'VR'")
    reason: str = Field(description="One sentence explanation")

def get_abs(markdown_path: str):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_abstract = False
    abstract_lines = []
    for line in lines:
        if line.strip().lower() == "## abstract":
            in_abstract = True
            continue
        if line.startswith("## ") and in_abstract:
            break
        if in_abstract:
            abstract_lines.append(line.strip())

    abstract = " ".join(abstract_lines).strip()
    return abstract

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract topics from text using Gemini API.")
    parser.add_argument("--save_dir", type=str, default=os.getcwd() + "/clone", help="Directory to save papers")
    parser.add_argument("--conf", type=str, default="cvpr", help="Conference name")
    parser.add_argument("--year", type=str, nargs='+', default=["2025"], help="Conference year(s)")
    
    args = parser.parse_args()
    conf_name = args.conf.upper()

    model = Transformers(MODEL, device_map="cuda")
    print(f"Loaded model {MODEL}.")

    for year in args.year:
        conf_dir = os.path.join(args.save_dir, f"{conf_name}{year}")
        extract_dir = os.path.join(conf_dir, 'topics')
        os.makedirs(extract_dir, exist_ok=True)

        if not os.path.exists(conf_dir):
            print(f"Directory {conf_dir} does not exist. Skipping...")
            continue

        print(f"Extracting topics for texts in {conf_dir}...")

        docling_main_dir = os.path.join(conf_dir, 'docling_main')
        if not os.path.exists(docling_main_dir):
            print(f"Directory {docling_main_dir} does not exist. Skipping...")
            continue
        mds = glob(os.path.join(docling_main_dir, "*.md"))

        for md_path in alive_it(mds, title="Processing markdown files"):

            filename = os.path.basename(md_path).replace('.md', '.json')
            json_path = os.path.join(extract_dir, filename)
            if os.path.exists(json_path):
                if VERBOSE:
                    print(f"Output for {md_path} already exists. Skipping...")
                continue
            
            if VERBOSE:
                print(f"Processing {md_path}...")
            
            abstract = get_abs(md_path)
            if not abstract:
                print(f"No abstract found in {md_path}. Skipping...")
                continue
            
            prompt_filled = USER_PROMPT.format(abstract)

            _model = model.copy()
            
            with system():
                _model += SYSTEM_PROMPT

            with user():
                _model += prompt_filled

            with assistant():
                _model += gen_json(name="result", schema=TopicExtractionResult)
            
            if VERBOSE:
                print("Sample output:", _model['result'])

            output_text = _model['result']
            output_text = TopicExtractionResult.model_validate_json(output_text).model_dump_json()
            output_json = json.loads(output_text)
            output_json['abstract'] = abstract

            if VERBOSE:
                print("Output JSON:", output_json)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output_json, f, indent=2)