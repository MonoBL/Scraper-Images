import os 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import shutil

def run_scraper(base_url, nmr_pagina, job_state):
        
    """
    #Url fornecido pelo o User
    base_url="https://www.vecteezy.com/free-photos/light-leaks?license-free=true"

    #numero de pagina a percorer 
    nmr_pagina= 3 """

    #Nome da pasta onde salvar
    download_folder_name= os.path.join(os.getcwd(), "vecteezy_downloads")
    download_path= os.path.join(download_folder_name, f"scrape_{int(time.time())}")

    # --- definir aqui quantos assets queremos recolher para teste
    # defina um inteiro (ex: 3) para testar só os primeiros N assets, ou None para todos
    max_asset = 2

    os.makedirs(download_path, exist_ok=True)
    print(f"Folder {download_path} created")

    #cria um objeto para as prefs que queremos 
    chrome_options= Options()
    #defenilas 
    prefs={
        "download.default_directory": download_path, #usar a folder como default
        "download.prompt_for_download":False, #evita a pergunta onde fazer download
        "download.directory_upgrade":True, #permite download para directorio diretamente
        "safebrowsing.enabled":True, #mantem seguro
        "safebrowsing.disable_download_protection":True,#desativa a proteção de download
        "profile.default_content_setting_values.cookies": 1 #aceita cookies mesmo que o o pop up contiue a aparecer
    }

    chrome_options.add_experimental_option("prefs",prefs)
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")  # ← NOVO: User agent


    #cria pasta para donwload usar o OS para criar e prcourar paasta
    
    driver = None #start diver como None 

    try:
        #start selenium drivers para abrir uma pagina no chorome
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 45)#define 15s para a pagina carregar toda

        print("google page open on headless")
        #criar o primeiro state
        job_state['status'] = 'finding_links'

        #salvar o link the todos os assets 
        link_assets=[]

        #loop para a pagina 1 ate a pagina defenida 
        for page_num in range(1, int(nmr_pagina) +1):
            #monta o url da pagina com o base mais o endereço da pagina e numero 
            url_pag= f"{base_url}&page={page_num}"
            print(f"Processing page {page_num} with url: {url_pag}")

            #driver vai dar start na pagina
            driver.get(url_pag)

            try:
                #esperar que a pagina carregue com a ajuda da div "ul.ez-resource-grid--main-grid"
                #garante que a pagina esta aberta
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.ez-resource-grid--main-grid")))
                time.sleep(2)#pausa para garantir que tudo abriu 

                #encontrar os elementos que contem o link 
                #usar a class exata onde esta o link
                link_element= driver.find_elements(By.CSS_SELECTOR, "a.ez-resource-thumb__link")
                print(f"Encontrados {len(link_element)} links de assets nesta pagina")

                #para cada elemento encontrado vamos contruir o url completo, isto ira criar os url estao vai estar os botoes de downlaod 
                for elemento in link_element:
                    link_final=elemento.get_attribute('href')
                    
                    if link_final and "vecteezy.com/" in link_final:
                        if link_final not in link_assets:
                            link_assets.append(link_final)
                    else:
                        print(f"Link ignorado: {link_final}")

            except Exception as e:
                print(f"Err procecing page num {page_num} err = {e}")
            
        print(f"\nFind {len(link_assets)} link assets for donwload.")


        # aplicar limite simples (se definido) — corta a lista para os primeiros N
        if max_asset is not None:
            try:
                n = int(max_asset)
                if n > 0:
                    link_assets = link_assets[:n]
                    print(f"Limitado para os primeiros {n} assets para teste.")
            except Exception:
                pass

       #atualizar o state com o numero max assets encontrados 
        total_assets= len(link_assets)
        job_state['status']= 'downloading'
        job_state['progress']= f'0/{link_assets}'

        print("\n---starting downloads---")
        #criação def reutilizaveis em vez de um loop para procurar e esperar downloads

        #função que espera que o donwload termina vendo se a pasta recebeu o ficheiro 

        def wait_downlads(folder, timeout=120):
            """Aguarda até não haver arquivos temporários (.crdownload, .part) na pasta ou até timeout."""
            waited = 0
            sleep_interval = 1
            while waited < timeout:
                files = os.listdir(folder)
                if any(f.endswith('.crdownload') or f.endswith('.part') for f in files):
                    time.sleep(sleep_interval)
                    waited += sleep_interval
                else:
                    return True
            return False

        def opt_download(driver, wait):
            #otimização vai dereto para os botoes de tamanho 
            #FLUXO:
            #1. Procura botões de tamanho (size buttons)
            #2. Clica no primeiro
            #3. Procura botão de download final
            #4. Clica e inicia download
            try: 
                #procurar botoes de tamanho
                print("Search for size buttons")

                #Espera 5s para os botoes aparecerem
                size_buttons = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.download-button__size-option'))
                )
                
                if size_buttons:

                    print(f"Buttons find: {len(size_buttons)}")

                    #clicar no primerio botão
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", size_buttons[0])
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", size_buttons[0])
                        print("clicked")
                        time.sleep(2) #Esperar abrir
                    except Exception as e:
                        print(f"Fail to click : {e}")
                    
                    try:
                        #prcurar botao com texto de download ou baixar
                        xpath_download="//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'baixar')]"
                        
                        btn_download=WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath_download)))
                        
                        if btn_download:
                            print("btn found")

                            #clicar no butao
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", btn_download)
                                time.sleep(0.3)
                                driver.execute_script("arguments[0].click();", btn_download)
                                print("Clicked on btn")
                                time.sleep(2)
                                return True
                            except Exception as e:
                                print(f"Failled to click, Err: {e}")
                                return False
                            
                    except Exception as e:
                        print(f"No Button find: {e}")
                        return False
                
                else:
                    print("No size button found ")
                    return False
                
            except Exception as e:
                print("Error in optimized download")
                return False


        print("\n---starting downaloads---")

        for i, assets_link in enumerate(link_assets): #loop para cada link recolhido e da duas variaveis sendo i o numero de cada um e o asset o url 
            print(f"\nProcessing assets {i+1}/{len(link_assets)}: {assets_link}")

            #atualizar o progress a cada loop ou seja depois de cada asset
            job_state['progress']= f'{i+1}/{total_assets}'

            try:
                #go to the page asset
                driver.get(assets_link)
                time.sleep(2) #load page

                success= opt_download(driver, wait)

                if success:
                    print("Donwload initiated ")

                    print("Wainting download")
                    if wait_downlads(download_path, timeout=60):
                        print(f"Donwload done")
                    else:
                        print("Download timeout (may still be downloading)")
                else:
                    print("Download failed to start")
            except Exception as e:
                print(f"Error on assets: {e}")
            
            #pausa entre assets
            time.sleep(3)
            
    except Exception as e:
        print(f"Error durring scrap {e}")
        #atualizar o state se tiver algum erro
        job_state['status']='error'
        job_state['error']= str(e)
        if driver:
            driver.quit()
        return#acaba mais cedo

    finally:
        #vai executar mesmo que erro
        if driver:
            print("Clossing")
            driver.quit()

    #zip the files
    print("Zipping the files")
    shutil.make_archive(f"{download_path}", 'zip', download_path)
    zip_path= f"{download_path}.zip"
    print(f"Zip file creates: {zip_path}")

    #atualizar o state final jontamente com o zip path 
    job_state['status']='complete'
    job_state['zip_path']= zip_path
    print("Job done")
    print(f"Job State: {job_state}")