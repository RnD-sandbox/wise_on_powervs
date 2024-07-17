import fitz  # PyMuPDF
import os
import re


def is_page_number(text):
    """
    Check if the given text is a page number.
    This simple heuristic assumes that page numbers are usually numeric and standalone.
    """
    return text.isdigit()


def convert_pdf_to_markdown(pdf_path):
    doc = fitz.open(pdf_path)
    markdown = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        text = span["text"].strip()
                        # Remove undecodable characters
                        text = text.encode("ascii", "ignore").decode("ascii")

                        if is_page_number(text):
                            continue

                        font_size = span["size"]

                        # Adjust headings based on font size
                        if font_size > 20:
                            line_text += f"# {text}\n"
                        elif font_size > 16:
                            line_text += f"## {text}\n"
                        elif font_size > 12:
                            line_text += f"### {text}\n"
                        elif re.match(r"^\d+(\.\d+)*\s", text):  # Match numbered topics
                            line_text += f"- {text}\n"
                        else:
                            line_text += f"{text} "

                    markdown += line_text.strip() + "\n"
            markdown += "\n"
    return markdown


def save_text_as_md(text, md_path):
    with open(md_path, "w", encoding="utf-8") as md_file:
        md_file.write(text)


def convert_pdfs_in_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            md_filename = filename.replace(".pdf", ".md")
            md_path = os.path.join(output_folder, md_filename)

            markdown_text = convert_pdf_to_markdown(pdf_path)
            save_text_as_md(markdown_text, md_path)
            print(f"Converted {pdf_path} to {md_path}")


input_folder = "pdfs"
output_folder = "mds"

convert_pdfs_in_folder(input_folder, output_folder)
