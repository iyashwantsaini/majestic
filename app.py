import os
import re
import sys
import base64
import arxiv
import pandas as pd
from flask import Flask, redirect, url_for, flash, render_template,request
import requests
import pandas as pd
import math
from werkzeug.utils import secure_filename
from tika import parser

# mongo
from flask import session
import pymongo
from pymongo import MongoClient
import bcrypt
# mongo

titles_list = []
links_list = []
date_list = []
doi_list=[]
citation_list=[]
abstract_list=[]
author_list=[]

app = Flask(__name__)

# mongo
app.config['MONGO_DBNAME'] = 'phd'
app.config['MONGO_URI'] = 'mongodb://phd:phd123@cluster0-shard-00-00-1c9pi.mongodb.net:27017,cluster0-shard-00-01-1c9pi.mongodb.net:27017,cluster0-shard-00-02-1c9pi.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority'
mongo=MongoClient('mongodb://phd:pdh123@cluster0-shard-00-00-1c9pi.mongodb.net:27017,cluster0-shard-00-01-1c9pi.mongodb.net:27017,cluster0-shard-00-02-1c9pi.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority')
# mongo

@app.route("/")
def index():
    # if 'username' in session:
    #     return render_template("dashboard.html",username=session["username"])
    # else:
        return render_template('login.html')

@app.route('/login',methods=['POST'])
def login():

    username = request.form['username']
    password= request.form['password']

    # username=base64.b64encode(username.encode('utf-8',errors = 'strict'))
    # password=base64.b64encode(password.encode('utf-8',errors = 'strict'))

    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(password.encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            # return redirect(url_for('index'))
            return render_template("dashboard.html")
    
    return render_template('login.html', warning='Please enter correct username and password')

    # if username=='thapar' and password=='thapar':
    #     return render_template('dashboard.html')
    # else :
    #     return render_template('login.html', warning='Please enter correct username and password')

# @app.route('/register', methods=['POST', 'GET'])
# def register():
#     if request.method == 'POST':
#         users = mongo.db.users
#         existing_user = users.find_one({'name' : request.form['username']})

#         if existing_user is None:
#             hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
#             users.insert({'name' : request.form['username'], 'password' : hashpass})
#             session['username'] = request.form['username']
#             return redirect(url_for('index'))
        
#         return 'That username already exists!'

#     return render_template('register.html')

@app.route("/logout")
def logout():
    session.pop('username',None)
    del session['username']
    return redirect(url_for('index'))
    # return render_template("login.html")

@app.route("/searchengine")
def searchengine():
    return render_template("searchengine.html")

@app.route("/found",methods=['POST','GET'])
def found():
    branch = request.form['engine'] #ieee or arxiv
    keyword = request.form['keyword']
    noofresults = request.form['number']
    noofresults = int(noofresults)
    print('hello')
    branch=branch.lower()
    if branch=='arxiv':
        print('hi')
        result = arxiv.query(query=keyword,max_results=noofresults)
        data = pd.DataFrame(columns = ["Title",'Published Date','Download Link'])
        for i in range(len(result)):
          title = result[i]['title']
          arxiv_url = result[i]['arxiv_url']
          arxiv_url=arxiv_url.replace('abs','pdf')
          published = result[i]['published']
          data_tmp = pd.DataFrame({"Title":title, "Published Date":published, "Download Link":arxiv_url},index=[0])
          data = pd.concat([data,data_tmp]).reset_index(drop=True) #dataframe
        return render_template('searchengine.html',tables=[data.to_html(render_links=True,classes=['table table-bordered'])]);
    elif branch=='ieee':
        page_no = 1
        no = math.ceil(noofresults/25)
        for page_no in range(1, no+1):

            headers = {
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://ieeexplore.ieee.org",
                "Content-Type": "application/json",
            }
            payload = {
                "newsearch": True,
                "queryText": keyword,
                "highlight": True,
                "returnFacets": ["ALL"],
                "returnType": "SEARCH",
                "pageNumber": page_no
            }
            r = requests.post(
                    "https://ieeexplore.ieee.org/rest/search",
                    json=payload,
                    headers=headers
                )
            page_data = r.json()
            for record in page_data["records"]:
                titles_list.append(record["articleTitle"])
                links_list.append('https://ieeexplore.ieee.org'+record["documentLink"])
                date_list.append(record["publicationDate"])
                citation_list.append(record["citationCount"])
                #author_list.append(record["authors"])
                '''if record["doi"] == '' or None :
                    doi_list.append("none")
                else:
                    doi_list.append(record["doi"])'''
        
            d = {"Title": titles_list, "Link": links_list, "Publication Date": date_list,  "No of Citations" : citation_list }
            df = pd.DataFrame.from_dict(d)
            finaldf = df[:noofresults] #dataframe
            return render_template('searchengine.html',tables=[finaldf.to_html(render_links=True,classes=['table table-bordered'])]);
@app.route('/uploader',methods=['GET', 'POST']) ##called when new file is uploaded in UI
def uploader():
   if request.method == 'POST':
       
      #pdf = request.files['file']
        ok = request.files['file']
        ok.save(secure_filename(ok.filename))
        fp = ok.filename
        fp=fp.replace(' ','_')
        fp = re.sub('[()]', '', fp)
        
        raw_xml = parser.from_file(fp, xmlContent=True)
        body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
        body_without_tag = body.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>","").replace("<p />","")
        text_pages = body_without_tag.split("""<div class="page">""")[1:]
        num_pages = len(text_pages)
        new = open("doc.txt","w")
        #print(num_pages)
        if num_pages==int(raw_xml['metadata']['xmpTPg:NPages']) : #check if it worked correctly
         for i in range(num_pages):
           new.write(text_pages[i])
           new.write(" \n page_ended \n ")  
        return render_template('dashboard.html')
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# @app.route("/login")
# def login():
#     return render_template("login.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/analyse")
def analyse():
    return render_template("analyse.html")

@app.route("/wordcloud")
def wordcloud():
    return render_template("wordcloud.html")

@app.route("/summarization")
def summarization():
    return render_template("summarization.html")

@app.route("/qna")
def qna():
    return render_template("qna.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

if __name__ == "__main__":
    app.secret_key = 'phd123'
    app.run(debug=True,use_reloader=True)
