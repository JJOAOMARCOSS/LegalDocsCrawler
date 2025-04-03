import os
import pandas as pd

TXT_INPUT_FOLDER = "text_cases"
CSV_OUTPUT_FOLDER = "csv_cases"
os.makedirs(CSV_OUTPUT_FOLDER, exist_ok=True)

def convert_txt_to_csv(txt_path, csv_path):
    try:
        # Lê o arquivo TXT. Ajuste o delimitador conforme necessário.
        df = pd.read_csv(txt_path, delimiter="\t")  # Supondo que o delimitador seja tabulação
        df.to_csv(csv_path, index=False)  # Salva como CSV sem o índice
        print(f"✓ TXT convertido: {txt_path} -> {csv_path}")
    except Exception as e:
        print(f"❌ Erro ao converter {txt_path}: {str(e)}")

def convert_all_txts_in_folder():
    for filename in os.listdir(TXT_INPUT_FOLDER):
        if filename.endswith(".txt"):
            txt_path = os.path.join(TXT_INPUT_FOLDER, filename)
            csv_filename = filename.replace(".txt", ".csv")
            csv_path = os.path.join(CSV_OUTPUT_FOLDER, csv_filename)
            convert_txt_to_csv(txt_path, csv_path)

if __name__ == "__main__":
    convert_all_txts_in_folder()