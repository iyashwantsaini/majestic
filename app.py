import os
from flask import Flask, redirect, url_for, flash, render_template

app = Flask(__name__)

@app.route("/")
def index():
        return render_template("login.html")

# @app.route("/register")
# def register():
#     return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/searchengine")
def searchengine():
    return render_template("searchengine.html")

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
#     return render_template("profile.html")

if __name__ == "__main__":
    app.run(debug=True,use_reloader=True)