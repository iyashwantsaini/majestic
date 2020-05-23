import os
import re
import arxiv
import pandas as pd
from flask import Flask, redirect, url_for, flash, render_template,request
import requests
import pandas as pd
from PyDictionary import PyDictionary
# from flask_ngrok import run_with_ngrok
import math
from werkzeug.utils import secure_filename
from tika import parser
from transformers import pipeline
# from urllib import *
from gensim.summarization.summarizer import summarize
from keywords import TextRank4Keyword
from nlppreprocess import NLP
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from wordcloud import WordCloud,ImageColorGenerator
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

from io import BytesIO
import shutil
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin

#socketio
from flask_socketio import SocketIO, emit,send
# from flask_ngrok import run_with_ngrok
# import random 
# import time 
# import numpy

# import nltk
# from nltk.stem.lancaster import LancasterStemmer
# stemmer = LancasterStemmer()

# import numpy
# import tflearn
# import tensorflow
# import random
# import json
# import pickle
# import os
#socketio

titles_list = []
links_list = []
date_list = []
doi_list=[]
citation_list=[]
abstract_list=[]
author_list=[]
obj = NLP()
nlp = pipeline('question-answering')
app = Flask(__name__)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#socketio
# socketio = SocketIO( app )
# welcome_greetings = ["Hey","Howdy","Greetings and Salutations!","Hello","Hi there!","Hey I'm doing great .How are you?","Nice to meet you!","Long time no see","Look who it is!"]
# greetings=["hi","hey","how are you"]
#socketio

# role_users = db.Table('roles_users',
#     db.Column('user_id',db.Integer, db.ForeignKey('user.id')),
#     db.Column('role_id',db.Integer, db.ForeignKey('role.id'))
# )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    pdfs = db.relationship('PDFdata', backref='owner')
    # active = db.Column(db.Boolean)
    # confirmed_at = db.Column(db.DateTime)
    # roles = db.relationship('Role', secondary= roles_users, backref=db.backref('users', lazy='dynamic'))

class PDFdata(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    filename=db.Column(db.String(300))
    data=db.Column(db.LargeBinary)
    text=db.Column(db.Text)
    date_uploaded = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# class Role(RoleMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40))
#     description = db.Column(db.String(255))

class AdminModelView(ModelView):
    def is_accessible(self):
        if current_user.username=='thapar123':
            return True
        # return current_user.is_authenticated
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('dashboard'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

admin =Admin(app, index_view=MyAdminIndexView())
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(PDFdata, db.session))

# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    # remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                # login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, warning='Incorrect Username or Password')
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('register.html', form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    # user = User.query.filter_by(username=form.username.data).first()
    # FileContents.query.filter_by(id=1).first()
    pdfs = PDFdata.query.filter_by(user_id=current_user.id).order_by(PDFdata.date_uploaded.desc()).all()
    # return send_file(BytesIO(file_data.data),attachment_filename='flask.pdf',as_attachment=True)
    # if current_user.is_authenticated:

    return render_template("dashboard.html",current_user=current_user,pdfs=pdfs)
    # else:
        # redirect(url_for('login'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/searchengine")
@login_required
def searchengine():
    return render_template("searchengine.html",current_user=current_user)

@app.route("/found",methods=['POST','GET'])
@login_required
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
            return render_template('searchengine.html',tables=[finaldf.to_html(render_links=True,classes=['table table-bordered'])],current_user=current_user);

@app.route("/upload")
@login_required
def upload():
    pdfs = PDFdata.query.filter_by(user_id=current_user.id).order_by(PDFdata.date_uploaded.desc()).all()
    return render_template("upload.html",current_user=current_user,pdfs=pdfs)

@app.route('/uploader',methods=['GET', 'POST']) ##called when new file is uploaded in UI
@login_required
def uploader():
   if request.method == 'POST':
        ok = request.files['file']
        ok.save(secure_filename(ok.filename))
        fp = ok.filename
        name=current_user.username
        fp=fp.replace(' ','_')
        fp = re.sub('[()]', '', fp)
        raw_xml = parser.from_file(fp, xmlContent=True)
        body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
        body_without_tag = body.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>","").replace("<p />","")
        text_pages = body_without_tag.split("""<div class="page">""")[1:]
        num_pages = len(text_pages)

        #savedb
        # binarydata=ok.read()
        # pdf = PDFdata(filename=fp, data=binarydata, text=body_without_tag, date_uploaded=datetime.now(), user_id=current_user.id)
        pdf = PDFdata(filename=fp, date_uploaded=datetime.now(), user_id=current_user.id)
        db.session.add(pdf)
        db.session.commit()
        #savedb

        pa=str(fp).replace('.pdf','')+'.txt'
        new = open("static/pdf/"+str(name)+'_'+pa,"w",encoding="utf-8")
        #print(num_pages)
        if num_pages==int(raw_xml['metadata']['xmpTPg:NPages']) : #check if it worked correctly
         for i in range(num_pages):
           new.write(text_pages[i])
           new.write(" \n page_ended \n ") 
        no=os.getcwd()
        plis=no+'/'+str(fp)
        filedir = "static/pdf/"
        shutil.move(plis,filedir)
        ren_src="static/pdf/"+str(fp)
        ren_des="static/pdf/"+current_user.username+'_'+str(fp)
        os.rename(ren_src,ren_des)
        
        return redirect(url_for('upload'))

@app.route("/analyse/<int:pdf_id>")
@login_required
def analyse(pdf_id):
    pdf = PDFdata.query.filter_by(id=pdf_id).one()
    return render_template("analyse.html",current_user=current_user, pdf=pdf)

@app.route("/wordcloud/<int:pdf_id>")
@login_required
def wordcloud(pdf_id):
    pdf = PDFdata.query.filter_by(id=pdf_id).one()
    fname=str(pdf.filename)
    fname1=fname.replace('.pdf','')
    uname=str(current_user.username)
    img='static/pdf/'+uname+'_'+fname1+'.txt'
    file = open(img,"r",encoding='utf-8') 
    text=file.read()
    stopwords = ['what','who','is','a','at','is','he']
    querywords = text.split()
    resultwords  = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)
    result=obj.process(result)
    # plot the WordCloud image	of overall document		
    char_mask = np.array(Image.open("heart.jpg"))
    image_colors = ImageColorGenerator(char_mask)
    wordcloud = WordCloud(background_color="white", max_words=100, width=250, height=250, mask=char_mask, random_state=2).generate(result)# to recolour the image		 
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud.recolor(color_func=image_colors))
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    plt.savefig('static/images/'+uname+'_'+fname1+'img1'+'.png')
    plt.clf()
    plt.cla()
    
    
    #plot the keywords according to text rank 
    
    tr4w = TextRank4Keyword()
    tr4w.analyze(result, candidate_pos = ['NOUN', 'PROPN'], window_size=4, lower=False)
    ok=tr4w.get_keywords(8)
    plt.bar(x=ok[0],height=ok[1], width = 0.7, color = ['grey', 'pink'] )
    
    #plt.figure(figsize=(250,250))
    #plt.show()
    plt.tight_layout(pad = 0)
    #print(ok[0],ok[1])
    
# naming the x-axis 
    plt.xlabel('IMPORTANT KEYTERMS') 
# naming the y-axis 
    plt.ylabel('KEYWORD SCORE') 
     
# plot title 
    #plt.title('My bar chart!')   
# function to show the plot 
    #plt.show() 
    plt.savefig('static/images/'+uname+'_'+fname1+'_'+'img2'+'.png')
    plt.close()
    return render_template("wordcloud.html",name = 'new_plot', url1 ='../static/images/'+uname+'_'+fname1+'img1'+'.png',url2 ='../static/images/'+uname+'_'+fname1+'_'+'img2'+'.png', pdf=pdf, current_user=current_user)

@app.route("/summarization/<int:pdf_id>")
@login_required
def summarization(pdf_id):
    pdf = PDFdata.query.filter_by(id=pdf_id).one()
    fname=str(pdf.filename)
    fname1=fname.replace('.pdf','')
    uname=str(current_user.username)
    img='static/pdf/'+uname+'_'+fname1+'.txt'
    file = open(img,"r",encoding='utf-8') 
    text=file.read()
    #print(text)
    new=text.split('page_ended')
    #new=obj.process(new)
    summary_list=[]
    no=len(new)
    for i in range(no-1):
        temp=new[i]
        #temp=obj.process(temp)
        summ=summarize(temp,word_count=150)
        summary_list.append(summ)
    return render_template('summarization.html',summary=summary_list, length = len(summary_list),pdf=pdf, current_user=current_user)


@app.route("/qna/<int:pdf_id>")
@login_required
def qna(pdf_id):
    ques= request.form["ques"]
    pdf = PDFdata.query.filter_by(id=pdf_id).one()
    fname=str(pdf.filename)
    fname1=fname.replace('.pdf','')
    uname=str(current_user.username)
    img='static/pdf/'+uname+'_'+fname1+'.txt'
    file = open(img,"r",encoding='utf-8') 
    text=file.read()
    ans=nlp({
    'question': ques,
    'context': text})
    new=ans['answer']
    return render_template("qna.html",current_user=current_user, pdf=pdf,answer=new)

@socketio.on('message')
def handleMessage(msg):
      msg =msg.lower()
      dictionary=PyDictionary()
      ok=dictionary.meaning(msg)
      ok1=list(dictionary.meaning(msg))
      l=['Noun','Verb','Adjective']

      if ok1 in l:
          ele=ok1[0]
          if ele =='Noun':
              val=ok['Noun'][0]
          elif ele=='Adjective':
              val=ok['Adjective'][0]
          elif ele=='Verb':
              val=ok['Verb'][0]
      
      send(val)
#socketio
# @app.route( '/' )
# def hello():
#   return render_template( 'index.html' )

# def bag_of_words(s, words):
#     bag = [0 for _ in range(len(words))]

#     s_words = nltk.word_tokenize(s)
#     s_words = [stemmer.stem(word.lower()) for word in s_words]

#     for se in s_words:
#         for i, w in enumerate(words):
#             if w == se:
#                 bag[i] = 1
            
#     return numpy.array(bag)

# @socketio.on('message')
# def handleMessage(msg):
#     msg =msg.lower()
    

#     with open("intents.json") as file:
#         data = json.load(file)

#     try:
#         with open("data.pickle", "rb") as f:
#             words, labels, training, output = pickle.load(f)
#     except:
#         words = []
#         labels = []
#         docs_x = []
#         docs_y = []
    
#         for intent in data["intents"]:
#             for pattern in intent["patterns"]:
#                 wrds = nltk.word_tokenize(pattern)
#                 words.extend(wrds)
#                 docs_x.append(wrds)
#                 docs_y.append(intent["tag"])
    
#             if intent["tag"] not in labels:
#                 labels.append(intent["tag"])
    
#         words = [stemmer.stem(w.lower()) for w in words if w != "?"]
#         words = sorted(list(set(words)))
    
#         labels = sorted(labels)
    
#         training = []
#         output = []
    
#         out_empty = [0 for _ in range(len(labels))]
    
#         for x, doc in enumerate(docs_x):
#             bag = []
    
#             wrds = [stemmer.stem(w.lower()) for w in doc]
    
#             for w in words:
#                 if w in wrds:
#                     bag.append(1)
#                 else:
#                     bag.append(0)
    
#             output_row = out_empty[:]
#             output_row[labels.index(docs_y[x])] = 1
    
#             training.append(bag)
#             output.append(output_row)
    
    
#         training = numpy.array(training)
#         output = numpy.array(output)
    
#         with open("data.pickle", "wb") as f:
#             pickle.dump((words, labels, training, output), f)

#     tensorflow.reset_default_graph()
    
#     net = tflearn.input_data(shape=[None, len(training[0])])
#     net = tflearn.fully_connected(net, 8)
#     net = tflearn.fully_connected(net, 8)
#     net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
#     net = tflearn.regression(net)
    
#     model = tflearn.DNN(net)
    
#     MODEL_NAME='model.tflearn'
#     if os.path.exists(MODEL_NAME + ".meta"):
#         model.load(MODEL_NAME)
#     else:
#         model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
#         model.save(MODEL_NAME)
        
#     results = model.predict([bag_of_words(msg, words)])
#     results_index = numpy.argmax(results)
#     tag = labels[results_index]

#     for tg in data["intents"]:
#             if tg['tag'] == tag:
#                 responses = tg['responses']

#     send(random.choice(responses))
#socketio

if __name__ == "__main__":
    db.create_all()
    # app.run(debug=True,use_reloader=True)
    app.run(debug=True)
    socketio.run( app, debug = True )
