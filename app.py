import os
import arxiv
import pandas as pd
from flask import Flask, redirect, url_for, flash, render_template,request
import requests
import pandas as pd
import math

titles_list = []
links_list = []
date_list = []
doi_list=[]
citation_list=[]
abstract_list=[]
author_list=[]

app = Flask(__name__)

@app.route("/")
def index():
        
        return render_template("login.html")

@app.route('/selection',methods=['POST'])
def selection():
    
    username = request.form['username']
    password= request.form['password']
    
    if username=='thapar' and password=='thapar':
        return render_template('dashboard.html')
    else :
        return render_template('login.html', warning='Please enter correct username and password')
    
    
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
        

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

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
    app.run()
