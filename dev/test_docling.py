from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionResult
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

import json

source = 'sample.pdf'

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
result: ConversionResult = converter.convert(source)

dict_result = result.document.export_to_dict()

with open('test_docling_output.json', 'w') as f:
    json.dump(dict_result, f, indent=4)

markdown_output = result.document.export_to_markdown(
    image_placeholder=''
)

with open('test_docling_output.md', 'w') as f:
    f.write(markdown_output)

html_output = result.document.export_to_html()

with open('test_docling_output.html', 'w') as f:
    f.write(html_output)

doctags_output = result.document.export_to_doctags()

with open('test_docling_output.doctags', 'w') as f:
    f.write(doctags_output)