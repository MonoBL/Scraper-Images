import os 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

#Url fornecido pelo o User
base_url="https://www.vecteezy.com/free-photos/light-leaks?license-free=true"

#numero de pagina a percorer 
nmr_pagina= 1

#Nome da pasta onde salvar
folder_name= os.path.join(os.getcwd(), "vecteezy_downloads")

#main domain
main_domain="https://www.vecteezy.com"



#cria um objeto para as prefs que queremos 
chorome_option= Options()
#defenilas 
prefs={
    "download.default_directory": folder_name, #usar a folder como default
    "download.prompt_for_download":False, #evita a pergunta onde fazer download
    "download.directory_upgrade":True, #permite download para directorio diretamente
    "safebrowsing.enabled":True, #mantem seguro
    "safebrowsing.disable_download_protection":True,#desativa a proteção de download
    "profile.default_content_setting_values.cookies": 1 #aceita cookies mesmo que o o pop up contiue a aparecer
}

chorome_option.add_experimental_option("prefs",prefs)
chorome_option.add_argument("--start-maximized")
#headless mode
#chorome_option.add_argument("--headless")

#cria pasta para donwload usar o OS para criar e prcourar paasta
if not os.path.exists(folder_name):
    os.makedirs(folder_name, exist_ok=True)
    print(f"Folder {folder_name} created")

#start selenium drivers para abrir uma pagina no chorome
driver = webdriver.Chrome(options=chorome_option)
wait = WebDriverWait(driver, 15)#define 15s para a pagina carregar toda

print("google page open")

#salvar o link the todos os assets 
link_assets=[]

#loop para a pagina 1 ate a pagina defenida 
for page_num in range(1, nmr_pagina +1):
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

print("\n---starting downloads---")
#criação def reutilizaveis em vez de um loop para procurar e esperar downloads

#função que espera que o donwload termina vendo se a pasta recebeu o ficheiro 
"""def wait_downlads(folder,timeout=120):
    waited=0 #variavel com valor de 0
    sleep_interval=1
    while waited<timeout: #loop roda enquando o waited nao bater 120 ou or o download for feito
        if any(f.endswith('.crdownload') or f.endswith('.part') for f in os.listdir(folder)): #any pergunta se tem algum desses ficheiro da pasta retorna T or F
            #se returnar true adiciona 1 ao waited 
            time.sleep(sleep_interval)
            waited+=sleep_interval
        else: #se o any responder false returna um true significa que o download terminou
            return True
    return False #chega aqui pq o waited chegou aos 120s
"""    

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

def find_download(driver, wait, timeout=8):
    """Tenta localizar o link/elemento final que dispara o download.

    Retorna uma tuple (type, value):
      - ('href', href) se encontrou um link direto
      - ('element', WebElement) se encontrou um elemento clicável
      - (None, None) se não encontrou
    """
    end_time = time.time() + timeout

    # 1) procurar links com classe óbvia
    try:
        a = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'download-button') or contains(@class,'download')]")))
        href = a.get_attribute('href')
        if href:
            print(f"Encontrado download link (class): {href}")
            return ('href', href)
        return ('element', a)
    except Exception:
        pass

    # 2) procurar anchors com atributo download
    try:
        anchors = driver.find_elements(By.CSS_SELECTOR, 'a[download]')
        for an in anchors:
            href = an.get_attribute('href')
            if href:
                print(f"Encontrado download link (a[download]): {href}")
                return ('href', href)
            return ('element', an)
    except Exception:
        pass

    # 3) procurar qualquer anchor cujo href contenha 'download' ou termine com extensão de arquivo comum
    try:
        anchors = driver.find_elements(By.TAG_NAME, 'a')
        for an in anchors:
            href = an.get_attribute('href')
            if not href:
                continue
            href_low = href.lower()
            if 'download' in href_low or href_low.endswith(('.zip', '.jpg', '.jpeg', '.png', '.gif', '.svg')) or 'cdn' in href_low:
                print(f"Encontrado download link (heurística href): {href}")
                return ('href', href)
    except Exception:
        pass

    # 4) procurar botões com texto que contenha 'download' ou 'baixar'
    try:
        xpath_txt = "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'baixar') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'free download')]"
        btn = driver.find_element(By.XPATH, xpath_txt)
        if btn:
            print("Encontrado botão com texto 'download'/'baixar'")
            return ('element', btn)
    except Exception:
        pass

    # 5) procurar elementos com atributos data-download
    try:
        el = driver.find_element(By.XPATH, "//*[@data-download or contains(@class,'download') or @aria-label='Download']")
        if el:
            href = el.get_attribute('href')
            if href:
                print(f"Encontrado download via atributo: {href}")
                return ('href', href)
            return ('element', el)
    except Exception:
        pass

    # 6) esperar um pouco e retornar None
    time.sleep(0.5)
    return (None, None)

def perfomance_url(driver):
    #retorna todos os url encontranos na window.performance.getEntries() com extensões comuns
    try:
        script='''
        const exts = ['.zip','.jpg','.jpeg','.png','.gif','.svg','.webp'];
        const entries = performance.getEntries() || [];
        return entries.map(e => e.name).filter(n => n && exts.some(ext => n.toLowerCase().includes(ext)));
        '''
        result=driver.execute_script(script)
        if result:
            return list(result)
    except Exception:
        pass
    return[]


#verifica se contem algum link de anuncio
def is_add(url):
    if not url: 
        return False #se tiver vazio nao é um anuncio 
    ad_signals= ['shutterstock', 'sa7eer', 'doubleclick', 'googlesyndication'] #lista de palavras que contem add
    low = url.lower()
    for s in ad_signals:
        if s in low:
            return True
    return False
    #pergunta se tem algumas das palavras dentro do url retunr true or false 


print("\n---starting downaloads---")

for i, assets_link in enumerate(link_assets): #loop para cada link recolhido e da duas variaveis sendo i o numero de cada um e o asset o url 
    print(f"\nProcessing assets {i+1}/{len(link_assets)}: {assets_link}")

    try:
        driver.get(assets_link)
        #1 clicar no botão principal
        try:
            botao_principal= wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ez-btn--primary[data-download-target='mainButton']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", botao_principal)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", botao_principal)
        except Exception:
            print("Main button not found, fiding another one")

        #2 vai procurar o link ou o botao de download
        try:
            #se a pagina tiver opção de tamanho pode levar ao botão de download
            try:
                size_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.download-button__size-option')
                if size_buttons:
                    print(f"Encontradas {len(size_buttons)} opções de tamanho, clicando na primeira...")
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", size_buttons[0])
                        time.sleep(1)
                    except Exception as e:
                        print(f"Falha ao clicar na opção de tamanho: {e}")
            except Exception:
                pass

            #Usar as funcções para encontrar algum link para download 
            target_type, target= find_download(driver, wait, timeout=8)
            if target_type== 'href' and target:
                if is_add(target):
                    print(f"Href detect as add ignoring: {target}")
                else:
                    print(f"downloading by href: {target}")
                    driver.get(target)
            elif target_type == 'element' and target:
                try:
                    wait.until(EC.element_to_be_clickable((By.XPATH, ".")))
                except Exception: 
                    pass
                try: 
                    #encontra elemento e clicka
                    driver.execute_script("arguments[0].scrollIntoView(true);", target)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", target)
                    print("Clicado no elemento de download final")
                except Exception as e:
                    print(f"FAil err: {e}")
            else:
                #def de performance para encontrar um link direto
                perf_url= perfomance_url(driver)
                if perf_url:
                    print("Resource find to download:")
                    chosen= None
                    for u in perf_url:
                        print(" - ", u)
                        if not is_add(u):
                            chosen=u
                            break
                    if chosen:
                        print(f"Going to recourse: {chosen}")
                        driver.get(chosen)
                    else:
                        print("All recouse are add/tracker")
                else:
                    print("No link find")
        except Exception as e:
            print(f"Error locating links to downalod\n Err: {e}")
        
        print("waiting downloads on folder")
        if wait_downlads(folder_name, timeout=60):
            print(f"Download end {folder_name}")
        else:
            print("Waiting download")

    except Exception as e:
        print(f"Err processing {assets_link}\n Err: {e}")
    
    time.sleep(4)

driver.quit()
print("\nfinish")

