from flask import Flask, render_template, request, send_file
from scraper import run_scraper
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    base_url = request.form['base_url']
    nmr_pagina = request.form['nmr_pagina']

    #roda o scrapper cria o path par ao zip file
    zip_path= run_scraper(base_url, nmr_pagina)
    
    #da o zip file para download 
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
