import os
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OUTPUT_FOLDER = "casesbii"
PROGRESS_FILE = "progress_bailii.json"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

SEARCH_TERMS_LIST = [
    '"modern slavery"',
    '"human trafficking"',
    '"forced labour"',
    "Slavery", "Slave", "Slaves", "Enslave", "Enslaved", "Enslavement",
    "Forced Labor", "Forced Work", "Forced Worker", "Forced Workers", "Forced Workforce",
    "Bonded Labor", "Bonded Work", "Bonded Worker", "Bonded Workers", "Bonded Workforce",
    "Debt Bondage", "Debt Enslavement", "Labor Trafficking", "Trafficking of Labor",
    "Trafficking of Workers", "Trafficking of Workforce", "Worker Trafficking",
    "Workers Trafficking", "Workforce Trafficking", "Coerced Labor", "Coerced Work",
    "Coerced Worker", "Coerced Workers", "Coerced Workforce", "Involuntary Labor",
    "Involuntary Work", "Involuntary Worker", "Involuntary Workers", "Involuntary Workforce",
    "Human Servitude", "Compulsory Labor", "Compulsory Work", "Compulsory Worker",
    "Compulsory Workers", "Compulsory Workforce", "Unfree Labor", "Unfree Work",
    "Unfree Worker", "Unfree Workers", "Unfree Workforce", "Child Labor", "Child Work",
    "Child Worker", "Child Workers", "Predatory Lending Exploitation", "Captive Labor",
    "Indentured Servitude", "Involuntary Servitude", "Constrained Labor", "Constrained Work",
    "Constrained Worker", "Constrained Workers", "Constrained Workforce", "Peonage",
    "Labor Bondage", "Coerced Debt Labor", "Servile Labor", "Exploited Labor",
    "Exploitation of Laborers", "Exploitation of Labor", "Exploitation of Workers",
    "Exploitation of Worker", "Worker Exploitation", "Workers Exploitation",
    "Exploited Worker", "Exploited Workers", "Exploited Workforce", "Exploitation of Workforce",
    "Workforce Exploitation", "Exploitation of Work", "Exploitation of Working Conditions",
    "sweatshop", "Worker abuse"
]

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")  # Ative se quiser rodar em segundo plano
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def save_content(driver, case_number, case_title, term, progress):
    try:
        time.sleep(2)
        pdf_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Printable PDF version') or contains(text(), 'Print-friendly')]")
            )
        )
        pdf_url = pdf_link.get_attribute('href')
        if not pdf_url.startswith('http'):
            pdf_url = f'https://www.bailii.org{pdf_url}'

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": driver.current_url
        }
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

        response = session.get(pdf_url, headers=headers, timeout=15)
        response.raise_for_status()

        safe_title = "".join(c for c in case_title if c.isalnum() or c in " _-")
        filename = f"{OUTPUT_FOLDER}/bailii_{term.replace(' ', '_').replace('\"', '')}_{case_number:04d}_{safe_title}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)

        progress[term]["processed_cases"].append(case_number)
        save_progress(progress)

        print(f"✓ PDF salvo: {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro salvando caso {case_number}: {str(e)[:200]}")
        return False

def process_results_page(driver, term, progress):
    results = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/cgi-bin/format.cgi?doc=')]"))
    )

    start_index = len(progress[term]["processed_cases"]) + 1

    for idx, result in enumerate(results, start=1):
        if idx in progress[term]["processed_cases"]:
            continue

        try:
            print(f"\n📄 Processando caso {idx}")
            case_title = result.text.split(']')[-1].strip()[:50]
            link = result.get_attribute('href')

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)

            if save_content(driver, idx, case_title, term, progress):
                print(f"✔️ Conteúdo salvo: {case_title}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

        except Exception as e:
            print(f"⚠️ Erro no caso {idx}: {e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Next 10 >>>']"))
        )
        next_button.click()
        print("\n➡️ Próxima página...")
        time.sleep(3)
        process_results_page(driver, term, progress)
    except:
        print("✅ Fim dos resultados.")

def main():
    progress = load_progress()
    driver = setup_driver()

    for term in SEARCH_TERMS_LIST:
        if term not in progress:
            progress[term] = {"processed_cases": []}

        if progress[term]["processed_cases"]:
            print(f"🔄 Pulando termo já processado: {term}")
            continue

        print(f"\n🔍 Buscando por: {term}")
        try:
            driver.get("https://www.bailii.org/")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Advanced Search"))
            ).click()

            search_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "query"))
            )
            search_field.clear()
            search_field.send_keys(term)
            driver.find_element(By.XPATH, "//input[@type='submit' and @value='Search']").click()
            process_results_page(driver, term, progress)

        except Exception as e:
            print(f"❌ Erro na busca por {term}: {e}")

    driver.quit()

if __name__ == "__main__":
    main()
