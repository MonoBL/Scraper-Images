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
