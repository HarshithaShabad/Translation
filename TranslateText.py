from flask import Flask, request, render_template
import os, requests, uuid, json, sys
import pandas as pd
import numpy as np
from pathlib import Path

def getFiles(src_folder):
    os.chdir(src_folder)
    return [
        name for name in os.listdir('.')
        if os.path.isfile(name)
    ]

def removeSpecialCharacters(full_file_name):
	text1 = request.form['text']
	src_path = text1.replace("\\", "/")
	with open(full_file_name, 'r', encoding ="UTF-16") as f:
		with open(src_path+"fixed.json", 'w+', encoding ="UTF-16") as template:
			for line in f:
				line = line.rstrip('\r\n')
				template.writelines(line)

def readfileJson():
	text1 = request.form['text']
	src_path = text1.replace("\\", "/")
	empty = "empty"
	if os.stat(src_path + "fixed.json").st_size != 0:
		jsonfile = open(src_path + "fixed.json", encoding ="UTF-16")
		jso = jsonfile.read()
		jsonfile.close()
		js = json.loads(jso)
		return js
	return empty

def get_translation(text,language_output):
    subscription_key = 'a5b9035a348e4583a6ea3065c3ddb4e0'
    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&to=' + language_output
    constructed_url = base_url + path + params
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    
    body = [{
        'text' : text
    }]
    response = requests.post(constructed_url, headers=headers, json=body)
    json_data = response.json()
    repository = json_data[0]
    repository = repository['translations']
    repository = repository[0]
    repository = repository['text']
    return repository
    
def main():
	text1 = request.form['text']
	src_path = text1.replace("\\", "/")
	src_files = getFiles(src_path)
	for file_name in src_files:
		full_file_name = os.path.join(src_path, file_name)
		file_name = Path(full_file_name).stem
		output_file_name = file_name+"_output.json"
		removeSpecialCharacters(full_file_name)
		js = readfileJson()
		if js != "empty":
			for i in range(0, len(js)):
				eng_trans = {"english_translated":get_translation(js[i]['TO_TRANSLATE'], 'en')} 
				js[i].update(eng_trans)
				with open(output_file_name, 'w+', encoding='UTF-16') as outfile:
					json.dump(js, outfile, ensure_ascii=False)
					if os.path.exists("fixed.json"):
						os.remove("fixed.json")


app = Flask(__name__)

@app.route('/TranslateText')
def my_form():
    return render_template('myform.html')

@app.route('/TranslateText', methods=['POST'])
def my_form_post():
    text1 = request.form['text']
    src_path = text1.replace("\\", "/")
    msg = "Translation Successful!"
    main()
    return msg

