from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os

SEARCH_TERMS = '"modern slavery" OR "human trafficking" OR "forced labour"'
OUTPUT_FOLDER = "cases"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

def save_content(driver, case_number, case_title):
    try:
        # Aguarda alguns segundos para garantir que a página foi carregada
        time.sleep(3)
        # Utiliza um XPath mais robusto para encontrar o link do PDF
        pdf_link = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Printable PDF version') or contains(text(), 'Print-friendly')]")
            )
        )
        pdf_url = pdf_link.get_attribute('href')
        
        # Corrige a URL se necessário
        if not pdf_url.startswith('http'):
            pdf_url = f'https://www.bailii.org{pdf_url}'
        
        # Verifica se a URL do PDF é válida
        if not pdf_url:
            print(f"❌ URL inválida para o caso {case_number}")
            return False

        # Configura headers reais com a URL atual da página
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": driver.current_url
        }

        # Cria uma sessão e adiciona os cookies do Selenium
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        
        # Tenta baixar o PDF com timeout e tratamento de exceção
        try:
            response = session.get(pdf_url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Falha ao baixar PDF do caso {case_number}: {e}")
            return False

        # Salva o PDF em disco
        safe_title = "".join(c for c in case_title if c.isalnum() or c in " _-")
        pdf_filename = f"{OUTPUT_FOLDER}/case_{case_number}_{safe_title}.pdf"
        
        with open(pdf_filename, "wb") as f:
            f.write(response.content)

        print(f"✓ Caso {case_number} salvo: {safe_title}")
        return True

    except Exception as e:
        print(f"Erro ao salvar caso {case_number}: {str(e)[:200]}")
        return False

def process_results_page(driver):
    try:
        results = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@href, '/cgi-bin/format.cgi?doc=')]")
            )
        )
        
        for idx, result in enumerate(results, start=1):
            try:
                print(f"\nProcessando caso {idx}")
                case_title = result.text.split(']')[-1].strip()[:50]
                link = result.get_attribute('href')

                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                
                # Aguarda o carregamento da página
                time.sleep(3)

                if save_content(driver, idx, case_title):
                    print(f"Conteúdo do caso {idx} salvo")
                else:
                    print(f"Falha ao salvar o conteúdo do caso {idx}")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)  # Aguarda antes de processar o próximo caso

            except Exception as e:
                print(f"Erro no caso {idx}: {str(e)[:200]}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
        
        # Paginação: procura o botão "Next 10 >>>"
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='submit' and @value='Next 10 >>>']")
                )
            )
            next_button.click()
            print("\n--- Navegando para próxima página ---")
            time.sleep(5)  # Aguarda a nova página carregar
            process_results_page(driver)
            
        except Exception as e:
            print("\n--- Última página alcançada ---")

    except Exception as e:
        print(f"Erro na página de resultados: {str(e)}")

def main():
    driver = setup_driver()
    try:
        driver.get("https://www.bailii.org/")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Advanced Search"))
        ).click()

        search_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "query"))
        )
        search_field.send_keys(SEARCH_TERMS)
        
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Search']").click()
        process_results_page(driver)

    except Exception as e:
        print(f"Erro fatal: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
