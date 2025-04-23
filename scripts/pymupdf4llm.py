# pip install pymupdf4llm


import pymupdf4llm
import pathlib

pdf_to_markdown = pymupdf4llm.pdf_to_markdown("pdf_file_path")
print(pdf_to_markdown)

output_file = pathlib.Path("pdf_file_path")
output_file.write_bytes(pdf_to_markdown.encode())


md_text_images = pymupdf4llm.to_markdown(
    doc="input_images.pdf",
    pages=[0, 2],
    page_chunks=True,
    write_images=True,
    image_path="images",
    image_format="png",
    dpi=300
)

md_text_words = pymupdf4llm.to_markdown(
    doc="input.pdf",
    pages=[0, 1, 2],
    page_chunks=True,
    write_images=True,
    image_path="images",
    image_format="png",
    dpi=300,
    extract_words=True
)