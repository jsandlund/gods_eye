# import the Flask class from the flask module
from flask import Flask, render_template
import time
import urllib2
import pymysql
import pandas.io.sql as psql
import pandas as pd
import logging
import re 
from bs4 import BeautifulSoup
from apiclient.discovery import build
from urllib2 import Request, urlopen
import json
import requests
conn = pymysql.connect(db='godseye',user='jsandlund',passwd='circleup2015',host='cuinstance.c5abr5owhqdm.us-east-1.rds.amazonaws.com')
from fullcontact import FullContact
from apiclient.discovery import build
import tldextract
from tld import get_tld
from fuzzywuzzy import fuzz

api_key = "AIzaSyB6F-v_KhoU6vhZRbii1ApUFRnuHxYKVGE"

service = build("customsearch", "v1",developerKey=api_key)

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
def home():
    print "hello world"

@app.route('/data')
def data():
    query = '''
    select firm_name,website_url
    from investor_company_url 
    where id < 10;'''
    url_data = psql.read_frame(query,conn)
    url_json = url_data.to_json()
    url_json_load = json.loads(url_json)
    return json.dumps(url_json_load)
    
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template
    

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
