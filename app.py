from flask import Flask, render_template, request, send_file, after_this_request
from scraper import run_scraper
import os
import shutil

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    base_url = request.form['base_url']
    nmr_pagina = request.form['nmr_pagina']

    # Roda o scraper e cria o arquivo ZIP
    zip_path = run_scraper(base_url, nmr_pagina)
    
    # Extrai o diretório que foi zipado (para deletar depois)
    download_folder = zip_path.replace('.zip', '')
    
    # Função para limpar arquivos após o download
    @after_this_request
    def cleanup(response):
        try:
            # Remove o arquivo ZIP
            if os.path.exists(zip_path):
                os.remove(zip_path)
                print(f"Deleted zip file: {zip_path}")
            
            # Remove a pasta de download
            if os.path.exists(download_folder):
                shutil.rmtree(download_folder)
                print(f"Deleted folder: {download_folder}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        return response
    
    # Envia o arquivo ZIP para download
    return send_file(zip_path, as_attachment=True, download_name=f"vecteezy_assets_{nmr_pagina}pages.zip")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')