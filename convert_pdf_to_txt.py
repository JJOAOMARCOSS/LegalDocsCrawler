import os
import PyPDF2

OUTPUT_FOLDER = "cases"
TXT_OUTPUT_FOLDER = "text_cases"
os.makedirs(TXT_OUTPUT_FOLDER, exist_ok=True)

def convert_pdf_to_txt(pdf_path, txt_path):
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
        
        print(f"✓ PDF convertido: {pdf_path} -> {txt_path}")
    except Exception as e:
        print(f"❌ Erro ao converter {pdf_path}: {str(e)}")

def convert_all_pdfs_in_folder():
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(OUTPUT_FOLDER, filename)
            txt_filename = filename.replace(".pdf", ".txt")
            txt_path = os.path.join(TXT_OUTPUT_FOLDER, txt_filename)
            convert_pdf_to_txt(pdf_path, txt_path)

if __name__ == "__main__":
    convert_all_pdfs_in_folder()