# import the Flask class from the flask module
from flask import Flask, render_template
import time
import urllib2
import pymysql
import pandas.io.sql as psql
import pandas as pd
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
    return "hello world"

@app.route('/data/firm')
def data_firm():
    query = '''
    select firm_name,website_url
    from investor_company_url 
    where result_rank = 0;'''
    url_data = psql.read_frame(query,conn)
    url_json = url_data.to_json()
    url_json_load = json.loads(url_json)
    return json.dumps(url_json_load)

@app.route('/data/prospects')
def data():
    query = '''
    select td.first_name,td.last_name,td.toofr_email,td.toofr_confidence,td.company_url,
    fc.rep_gender as gender,fc.rep_location as location,fc.rep_klout_score as klout_score,
    fc.rep_klout_topic as klout_topic,fc.rep_facebook_url as facebook_url,fc.rep_facebook_following as facebook_following,
    fc.rep_linkedin_url as linkedin_url,fc.rep_twitter_url as twitter_url,fc.rep_twitter_followers as twitter_followers,
    fc.rep_twitter_following as twitter_following,fc.rep_angellist_url as angellist_url,fc.rep_angellist_followers as angellist_followers
    from investor_toofr_data td
    JOIN fullcontact fc ON td.id=fc.toofr_id;'''
    toofr_fc_data = psql.read_frame(query,conn)
    toofr_fc_data_json = toofr_fc_data.to_json()
    toofr_fc_data_json = json.loads(toofr_fc_data_json)
    return json.dumps(toofr_fc_data_json)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
