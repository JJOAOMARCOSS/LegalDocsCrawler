import os
import subprocess

OUTPUT_FOLDER = "cases"
TXT_OUTPUT_FOLDER = "text_cases"
os.makedirs(TXT_OUTPUT_FOLDER, exist_ok=True)

def convert_pdf_to_txt(pdf_path, txt_path):
    try:
        # Usa o poppler para extrair texto do PDF
        result = subprocess.run(['pdftotext', pdf_path, txt_path], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erro ao converter {pdf_path}: {result.stderr}")
            return
        
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