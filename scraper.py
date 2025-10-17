import os 
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

#Url fornecido pelo o User
base_url="https://www.vecteezy.com/free-photos/light-leaks?license-free=true"

#numero de pagina a percorer 
nmr_pagina= 3

#Nome da pasta onde salvar
folder_name= "scraper_download"

#main domain
main_domain="https://www.vecteezy.com"

#cria pasta para donwload usar o OS para criar e prcourar paasta
if not os.path.exists(folder_name):
    os.mkdir(folder_name)
    print(f"Folder {folder_name} created")


#modo headless sem abrir pagina google descomentar 
#options = webdriver.ChoromeOptions()
#options.add_argument("--headless")
#driver =webdriver.Chorome(options=options)

#start selenium drivers para abrir uma pagina no chorome
driver = webdriver.Chorome()
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
        # selector "li.ez-resource-grid__item a" vai procurar as tag dentro das tags li com a class ez-resource-grid__item
        link_element= driver.find_elements(By.CSS_SELECTOR, "li.ez-resource-grid__item a")

        #para cada elemento encontrado vamos contruir o url completo, isto ira criar os url estao vai estar os botoes de downlaod 
        for elemento in link_element:
            link_relativo= elemento.get_attribute('href')

            #verifacar se contem link
            if link_relativo:
                #juntar o dominio mais o link para o link completo
                link_final=f"{main_domain}{link_relativo}"

                #adiconar ao dicionario apenas se nao estiver 
                if link_final not in link_assets:
                    link_assets.append(link_final)

    except Exception as e:
        print(f"Err procecing page num {page_num} err = {e}")
    
print(f"\nFind {len(link_assets)} link assets for donwload.")
