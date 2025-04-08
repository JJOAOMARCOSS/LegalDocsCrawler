import os
import pandas as pd

TXT_INPUT_FOLDER = "text_cases"
CSV_OUTPUT_FOLDER = "csv_cases"
os.makedirs(CSV_OUTPUT_FOLDER, exist_ok=True)
import os
import pandas as pd
import subprocess

TXT_INPUT_FOLDER = "text_cases"
CSV_OUTPUT_FOLDER = "csv_cases"
os.makedirs(CSV_OUTPUT_FOLDER, exist_ok=True)

def convert_txt_to_csv(txt_path, csv_path):
    try:
        # Lê o arquivo TXT
        with open(txt_path, 'r', encoding='utf-8') as file:
            plain_text = file.read()
        
        # Contagem de caracteres
        char_count = len(plain_text)

        # Extrai o nome do arquivo sem a extensão
        file_name = os.path.basename(txt_path).replace('.txt', '')

        # Cria um DataFrame com as informações necessárias
        df = pd.DataFrame({
            'ID': [file_name],  # Usando o nome do arquivo como ID
            'nome do arquivo': [file_name],
            'plain_text': [plain_text],
            'char_count': [char_count]  # Adiciona a contagem de caracteres
        })

        # Salva como CSV
        df.to_csv(csv_path, index=False)  # Salva como CSV sem o índice
        print(f"✓ TXT convertido: {txt_path} -> {csv_path} (Total de caracteres: {char_count})")
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