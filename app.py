from flask import Flask, render_template, request, send_file, after_this_request, jsonify
from scraper import run_scraper
import os
import shutil
import uuid
import threading

app = Flask(__name__)

#dicionario para guardar os dados de estado 
scrape_jobs={}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    base_url = request.form['base_url']
    nmr_pagina = request.form['nmr_pagina']

    #criar um ID unico com o UUID versao 4
    job_id = str(uuid.uuid4())

    #criar um dicionario base
    job_state={
        'status': 'starting',
        'progress': '0/0',
        'zip_path': None,
        'error': None
    }
    scrape_jobs[job_id]= job_state

    #Start a thread com um job state
    thread= threading.Thread(target=run_scraper, args=(base_url, nmr_pagina, job_state))
    thread.start()

    #devolver o job ID para o browser
    return jsonify({'status': 'started', 'job_id': job_id})


@app.route('/progress/<job_id>')
def get_progress(job_id):
    #endpoint para o JS ter acesso ao progress
    job=scrape_jobs.get(job_id)

    if not job:
        return jsonify({'status': 'not_found'}), 404
    
    return jsonify(job)

@app.route('/download/<job_id>')
def donwload_file(job_id):
    #endpoint para browser fazer downaload do zip
    job= scrape_jobs.get(job_id)
    if not job:
        return jsonify ({'status':'not found'}), 404
    
    if job ['status']== 'error':
        return jsonify({'status':'error',
                         'message': job['error']}), 500
    
    if job ['status'] != 'complete' or not job['zip_path']:
        return jsonify({'status':'processing', 'message': 'job still running or path not found'}), 422
    
    zip_path =job['zip_path']
    donwload_folder = zip_path.replace['.zip', '']

    #função para apagar arquivos downlaod 
    @after_this_request
    def clean(response):
        try:
            #remover o ZIP
            if os.path.exists(zip_path):
                os.remove(zip_path)
                print(f"File deleted {zip_path}")
            
            #remover download folder
            if os.path.exists(donwload_folder):
                shutil.rmtree(donwload_folder)
                print(f"Deleted folder: {donwload_folder}")

            #remover job id do dicionario
            if job_id in scrape_jobs:
                del scrape_jobs[job_id]
                print(f"Job id removed: {job_id}")

        except Exception as e:
            print(f"Err: {e}")

        return response
    
    #enviar o zip para download
    return send_file(zip_path, as_attachment=True, download_name=f"vecteezy_assets_{job_id[:8]}.zip")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
