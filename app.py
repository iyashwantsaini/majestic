import os
from flask import Flask, redirect, url_for, flash, render_template,request

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
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login():
    return render_template("login.html")

'''

@app.route("/wordcloud")
def wordcloud():
    return render_template("wordcloud.html")

@app.route("/summarization")
def summarization():
    return render_template("summarization.html")

@app.route("/qna")
def qna():
    return render_template("qna.html")

# @app.route("/profile")
# def profile():
#     return render_template("profile.html")'''

if __name__ == "__main__":
    app.run()
