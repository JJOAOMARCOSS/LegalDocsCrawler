from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import urllib.request
import json
import random

# Termos de busca usados no site
SEARCH_TERMS = '"modern slavery" OR "human trafficking" OR "forced labour"'

# Pasta onde os PDFs serão salvos
OUTPUT_FOLDER = "cases"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Arquivo para salvar progresso
PROGRESS_FILE = "progress.json"

# Quantidade de resultados a serem processados por bloco
BATCH_SIZE = 50

# Índice inicial (caso não exista o arquivo de progresso)
START_INDEX = 80

def setup_driver():
    """Configura o Chrome com diretório de download e outras opções."""
    options = webdriver.ChromeOptions()

    # Descomente abaixo para rodar em segundo plano (headless)
    # options.add_argument("--headless")

    prefs = {
        "download.default_directory": os.path.abspath(OUTPUT_FOLDER),
        "download.prompt_for_download": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def accept_cookies(driver):
    """Aceita cookies se o botão estiver disponível."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cookieConsentBlocker"))
        )
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all cookies')]"))
        )
        driver.execute_script("arguments[0].click();", accept_button)
        print("✓ Cookies aceitos com sucesso")
        time.sleep(3)
    except Exception as e:
        print("⚠️ Erro ao aceitar cookies:", str(e)[:100])

def baixar_pdf_directo(pdf_url, filename):
    """Baixa o PDF diretamente da URL e salva na pasta cases."""
    try:
        urllib.request.urlretrieve(pdf_url, filename)
        print(f"✔️ PDF salvo: {filename}")
    except Exception as e:
        print(f"❌ Falha ao baixar PDF direto: {e}")

def salvar_progresso(index):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"ultimo_indice": index}, f)

def carregar_progresso():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
            return data.get("ultimo_indice", START_INDEX)
    return START_INDEX

def espera_humana(min_s=4, max_s=8):
    time.sleep(random.uniform(min_s, max_s))

def pausa_longa():
    pausa = random.randint(300, 420)  # 5 a 7 minutos
    print(f"⏳ Pausa longa de {pausa // 60} minutos...")
    time.sleep(pausa)

def main():
    driver = setup_driver()
    try:
        driver.get("https://www.canlii.org/")
        accept_cookies(driver)

        search_box = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "textInput"))
        )
        search_box.send_keys(SEARCH_TERMS + Keys.RETURN)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-result-index]"))
        )

        indice_atual = carregar_progresso()

        while True:
            results = driver.find_elements(By.XPATH, "//a[@data-result-index]")

            while indice_atual >= len(results):
                try:
                    load_more = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[text()='Load more...']"))
                    )
                    driver.execute_script("arguments[0].click();", load_more)
                    print("🔄 'Load more...' clicado para carregar mais resultados.")
                    time.sleep(6)
                    results = driver.find_elements(By.XPATH, "//a[@data-result-index]")
                except:
                    print("✅ Nenhum botão 'Load more results' encontrado — fim dos resultados.")
                    return

            for _ in range(BATCH_SIZE):
                if indice_atual >= len(results):
                    break

                result = results[indice_atual]

                case_title = result.text.strip()[:50].replace(" ", "_").replace("/", "_")
                print(f"\n📄 Processando resultado {indice_atual + 1} - {case_title[:60]}...")

                driver.execute_script("window.open(arguments[0].href, '_blank');", result)
                WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                driver.switch_to.window(driver.window_handles[1])
                espera_humana(5, 10)

                try:
                    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                    if not pdf_links:
                        print("❌ Nenhum link para PDF encontrado.")
                    else:
                        pdf_url = pdf_links[0].get_attribute("href")
                        print(f"➜ Link do PDF: {pdf_url}")
                        filename = os.path.join(
                            OUTPUT_FOLDER,
                            f"{indice_atual+1:04d}_{case_title[:40]}.pdf"
                        )
                        baixar_pdf_directo(pdf_url, filename)
                except Exception as e:
                    print(f"❌ Erro ao tentar localizar/baixar PDF: {e}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                espera_humana()

                indice_atual += 1
                salvar_progresso(indice_atual)

            pausa_longa()

    except Exception as e:
        print("❌ Erro fatal:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
