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
nmr_pagina= 3

#Nome da pasta onde salvar
folder_name= os.path.join(os.getcwd(), "vecteezy_downloads")

#main domain
main_domain="https://www.vecteezy.com"



#cria um objeto para as prefs que queremos 
chorome_option= Options()
#defenilas 
prefs={
    "download.default_directory": folder_name, #usar a folder como default
    "download.prompt_for_download":True, #evita a pergunta onde fazer download
    "directory_upgrade":True, #permite download para directorio diretamente
    "safebrowsing.enabled":True, #mantem seguro
    "profile.default_content_setting_values.cookies": 1
}

chorome_option.add_experimental_option("prefs",prefs)
chorome_option.add_argument("--start-maximized")
#headless mode
#chorome_option.add_argument("--headless")

#cria pasta para donwload usar o OS para criar e prcourar paasta
if not os.path.exists(folder_name):
    os.mkdir(folder_name)
    print(f"Folder {folder_name} created")

#start selenium drivers para abrir uma pagina no chorome
driver = webdriver.Chrome(options=chorome_option)
wait = WebDriverWait(driver, 15)#define 15s para a pagina carregar toda

print("google page open")


#aceitar cookies, usar o try como so é preciso aceitar uma vez, se o botao nao aparecer o codigo continua
try:
    print("accepting coockies")
    driver.get(main_domain)

    time.sleep(2)

    #esperar o botao de aceitar aparecer
    botao_coockies=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.message-component-button[title="Accept"]')))

    #click em JS
    driver.execute_script("arguments[0].click();", botao_coockies)


    print("coocckies accept")
    time.sleep(2)
except TimeoutException:
    print("popup nao apareceu")
except Exception as e:
    print("no pop-up of coockies maybe already accepted")

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

print("\n---starting downaloads---")

#loop para fazer o click e download em cada um dos link gerados anterioremente
for i, link_assets in enumerate(link_assets):
    print(f"Processing asset links {i+1}/{len(link_assets)}: {link_assets}")

    try:
        #1 ir para a pagina do asset
        driver.get(link_assets)

        botao_donw=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.ez-btn--primary[data-download-target='mainButton']")))
        
        driver.execute_script("arguments[0].scrollIntoView(true);", botao_donw)
        time.sleep(1)
        #usar click via javascript para evitar crash
        driver.execute_script("arguments[0].click();", botao_donw)
        

        #esperar ecra de contagem e clicar em algum botão se necessarion
        try:
            link_download_final=wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'download-button')]")))
            link_download_final.click()
            print("Final button clicked")
        except:
            #if nao tiver nenhum botao esperar o download
            print("No button download started")

        print("Awating download")
        time.sleep(10) #esperar 10s

        print(f"Download fininsh for folder '{folder_name}'")
    except Exception as e:
        print(f"Err processing {link_assets} skiping, err: {e}")

    time.sleep(4) #espera 4s entre downloads 

driver.quit()
print("\nfinish")

