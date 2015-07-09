# import the Flask class from the flask module
from flask import Flask, render_template, request, url_for
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
    return render_template('locked.html')  # render a template

@app.route('/prospects/new/')
def newProspect():
    return render_template('prospects/new.html')  # render a template

@app.route('/prospects/')
def prospects():
    return render_template('prospects/index.html')  # render a template

@app.route('/leads/')
def leads():
    return render_template('leads/index.html')  # render a template

@app.route('/hello/', methods=['POST'])
def hello():
    first_name=request.form['firstName']
    last_name=request.form['lastName']
    company_url=request.form['companyUrl']
    source="Ad Hoc"
    api_key = "ddb2740f8d2338c78497519c13cc7076"
    params = {'key': api_key, 'domain': company_url, 'first': first_name , 'last' : last_name}

    toofr_url = "http://toofr.com/api/guess?"
    test = requests.get(toofr_url, params=params)
    toofr_data = test.json()

    try:
        toofr_email = toofr_data['response']['email']
    except:
        toofr_email = None
    try:
        toofr_confidence = toofr_data['response']['confidence']
    except:
        toofr_confidence = None
    toofr_data = pd.DataFrame(columns=('toofr_email','first_name','last_name','toofr_confidence','company_url','source'))

    existing_records_final_links = len(toofr_data)
    toofr_data.loc[existing_records_final_links] = [toofr_email,first_name,last_name,toofr_confidence,company_url,source]
    toofr_data.to_sql("investor_toofr_data",con=conn,flavor='mysql',if_exists='append',index=False)

    query = '''
    select td.id,td.toofr_email as email
    from investor_toofr_data td
    having td.id =  (select max(id)
                     from investor_toofr_data);'''

    toofr_data = psql.read_frame(query,conn)
    toofr_data_dict = {}
    toofr_data_dict = toofr_data.set_index('id').to_dict()
    toofr_data_dict = toofr_data_dict['email']

    for key,value in toofr_data_dict.items():
        fc = FullContact('76152464a239f71c')
        print key,value
        person_profile = fc.get(email=value)

        if person_profile['status'] == 200:
            rep_gender = None
            rep_location = None
            rep_klout_score = None
            rep_klout_topic = None
            rep_facebook_url = None
            rep_facebook_followers = None
            rep_facebook_following = None
            rep_linkedin_url = None
            rep_twitter_url = None
            rep_twitter_followers = None
            rep_twitter_following = None
            rep_angellist_url = None
            rep_angellist_followers = None

            try:
                rep_gender= person_profile['demographics']['gender']
            except:
                print 'gender_missing'
            try:
                rep_location = person_profile['demographics']['locationGeneral']
            except:
                print 'location_missing'

            try:
                rep_klout_score = person_profile['digitalFootprint']['scores'][0]['value']
            except:
                print 'klout score missing'
            try:
                rep_klout_topic= person_profile['digitalFootprint']['topics'][0]['value']
            except:
                print 'klout topic missing'

            try:
                rep_social_profiles = person_profile['socialProfiles']
                if len(rep_social_profiles) > 0:
                    for i in xrange(0,len(rep_social_profiles)):
                        if rep_social_profiles[i]['typeName']=='Facebook':
                            try:
                                rep_facebook_url = rep_social_profiles[i]['url']
                            except:
                                print 'facebook url missing'
                            try:

                                rep_facebook_followers= rep_social_profiles[i]['followers']
                            except:
                                print 'facebook followers missing'
                            try:
                                rep_facebook_following = rep_social_profiles[i]['following']
                            except:
                                print 'facebook following missing'
                        if rep_social_profiles[i]['typeName']=='LinkedIn':
                            try:
                                rep_linkedin_url = rep_social_profiles[i]['url']
                            except:
                                print 'linkedin url missing'
                        if rep_social_profiles[i]['typeName']=='Twitter':
                            try :
                                rep_twitter_url = rep_social_profiles[i]['url']
                            except:
                                print 'twitter url missing'
                            try:

                                rep_twitter_followers = rep_social_profiles[i]['followers']
                            except:
                                print 'twitter followers missing'
                            try:

                                rep_twitter_following = rep_social_profiles[i]['following']
                            except:
                                print 'twitter following missing'
                        if rep_social_profiles[i]['typeName']=='AngelList':
                            try:

                                rep_angellist_url= rep_social_profiles[i]['url']
                            except:
                                print 'angel list url missing'
                            try:

                                rep_angellist_followers = rep_social_profiles[i]['followers']
                            except:
                                print 'angel list followers missing'
            except:
                print 'no social profile found'

            data = pd.DataFrame(columns=('toofr_id','rep_gender','rep_location','rep_klout_score','rep_klout_topic','rep_facebook_url','rep_facebook_followers','rep_facebook_following',
                                         'rep_linkedin_url','rep_twitter_url','rep_twitter_followers','rep_twitter_following','rep_angellist_url','rep_angellist_followers'))

            existing_records_final_links = len(data)
            data.loc[existing_records_final_links] = [key,rep_gender,rep_location,rep_klout_score,rep_klout_topic,rep_facebook_url,rep_facebook_followers,rep_facebook_following,
            rep_linkedin_url,rep_twitter_url,rep_twitter_followers,rep_twitter_following,rep_angellist_url,rep_angellist_followers]
            data = data.where(pd.notnull(data), None)
            data.to_sql('fullcontact',con=conn,flavor='mysql',if_exists='append',index=False)
    return render_template('form_action.html', firstName=first_name, lastName=last_name)

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

@app.route('/data/prospects.json')
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
    test = toofr_fc_data.to_json(orient="index")
    toofr_fc_data_json = json.loads(test)
    return json.dumps(toofr_fc_data_json)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
