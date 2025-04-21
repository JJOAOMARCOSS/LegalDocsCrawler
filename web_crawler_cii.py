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

SEARCH_TERMS_LIST = [
    '"modern slavery"',
    '"human trafficking"',
    '"forced labour"',
    "Slavery", "Slave", "Slaves", "Enslave", "Enslaved", "Enslavement",
    "Forced Labor", "Forced Work", "Forced Worker", "Forced Workers", "Forced Workforce",
    "Bonded Labor", "Bonded Work", "Bonded Worker", "Bonded Workers", "Bonded Workforce",
    "Debt Bondage", "Debt Enslavement",
    "Labor Trafficking", "Trafficking of Labor", "Trafficking of Workers",
    "Trafficking of Workforce", "Worker Trafficking", "Workers Trafficking", "Workforce Trafficking",
    "Coerced Labor", "Coerced Work", "Coerced Worker", "Coerced Workers", "Coerced Workforce",
    "Involuntary Labor", "Involuntary Work", "Involuntary Worker", "Involuntary Workers", "Involuntary Workforce",
    "Human Servitude", "Compulsory Labor", "Compulsory Work", "Compulsory Worker", "Compulsory Workers", "Compulsory Workforce",
    "Unfree Labor", "Unfree Work", "Unfree Worker", "Unfree Workers", "Unfree Workforce",
    "Child Labor", "Child Work", "Child Worker", "Child Workers",
    "Predatory Lending Exploitation", "Captive Labor", "Indentured Servitude", "Involuntary Servitude",
    "Constrained Labor", "Constrained Work", "Constrained Worker", "Constrained Workers", "Constrained Workforce",
    "Peonage", "Labor Bondage", "Coerced Debt Labor", "Servile Labor", "Exploited Labor",
    "Exploitation of Laborers", "Exploitation of Labor", "Exploitation of Workers", "Exploitation of Worker",
    "Worker Exploitation", "Workers Exploitation", "Exploited Worker", "Exploited Workers", "Exploited Workforce",
    "Exploitation of Workforce", "Workforce Exploitation", "Exploitation of Work", "Exploitation of Working Conditions",
    "sweatshop", "Worker abuse"
]

OUTPUT_FOLDER = "cases"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

PROGRESS_FILE = "progress.json"
BATCH_SIZE = 25

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Ative se quiser rodar em segundo plano
    prefs = {
        "download.default_directory": os.path.abspath(OUTPUT_FOLDER),
        "download.prompt_for_download": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def accept_cookies(driver):
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
    except:
        pass

def baixar_pdf_directo(pdf_url, filename):
    try:
        urllib.request.urlretrieve(pdf_url, filename)
        print(f"✔️ PDF salvo: {filename}")
    except Exception as e:
        print(f"❌ Falha ao baixar PDF direto: {e}")

def salvar_progresso(indice, termo_index):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"ultimo_indice": indice, "termo_index": termo_index}, f)

def carregar_progresso():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
            return data.get("ultimo_indice", 0), data.get("termo_index", 0)
    return 0, 0

def espera_humana(min_s=4, max_s=8):
    time.sleep(random.uniform(min_s, max_s))

def pausa_longa():
    pausa = random.randint(300, 420)
    print(f"⏳ Pausa longa de {pausa // 60} minutos...")
    time.sleep(pausa)

def buscar(driver, termo, start_index):
    driver.get("https://www.canlii.org/")
    accept_cookies(driver)
    search_box = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "textInput"))
    )
    search_box.send_keys(termo + Keys.RETURN)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[@data-result-index]"))
    )
    
    indice_atual = start_index

    while True:
        results = driver.find_elements(By.XPATH, "//a[@data-result-index]")
        print(f"🔍 Total de resultados carregados até agora: {len(results)}")

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
                return indice_atual

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
            salvar_progresso(indice_atual, SEARCH_TERMS_LIST.index(termo))

        pausa_longa()

def main():
    start_index, termo_index = carregar_progresso()
    driver = setup_driver()

    try:
        for i in range(termo_index, len(SEARCH_TERMS_LIST)):
            termo = SEARCH_TERMS_LIST[i]
            print(f"\n🔎 Iniciando busca pelo termo: {termo}")
            start_index = buscar(driver, termo, start_index)
            salvar_progresso(0, i + 1)  # Reinicia índice e avança o termo
            start_index = 0
    except Exception as e:
        print("❌ Erro fatal:", str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
