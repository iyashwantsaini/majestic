import os
import re
import arxiv
import pandas as pd
from flask import Flask, redirect, url_for, flash, render_template,request
import requests
import pandas as pd
from flask_ngrok import run_with_ngrok
import math
from werkzeug.utils import secure_filename
from tika import parser

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin


titles_list = []
links_list = []
date_list = []
doi_list=[]
citation_list=[]
abstract_list=[]
author_list=[]

app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# role_users = db.Table('roles_users',
#     db.Column('user_id',db.Integer, db.ForeignKey('user.id')),
#     db.Column('role_id',db.Integer, db.ForeignKey('role.id'))
# )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    # active = db.Column(db.Boolean)
    # confirmed_at = db.Column(db.DateTime)
    # roles = db.relationship('Role', secondary= roles_users, backref=db.backref('users', lazy='dynamic'))

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
    # if current_user.is_authenticated:
    return render_template("dashboard.html",current_user=current_user)
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

@app.route('/uploader',methods=['GET', 'POST']) ##called when new file is uploaded in UI
@login_required
def uploader():
   if request.method == 'POST':
        ok = request.files['file']
        ok.save(secure_filename(ok.filename))
        fp = ok.filename
        fp=fp.replace(' ','_')
        fp = re.sub('[()]', '', fp)
        pa=str(fp).replace('.pdf','')+'.txt'
        raw_xml = parser.from_file(fp, xmlContent=True)
        body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
        body_without_tag = body.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>","").replace("<p />","")
        text_pages = body_without_tag.split("""<div class="page">""")[1:]
        num_pages = len(text_pages)
        new = open("PDF/"+pa,"w")
        #print(num_pages)
        if num_pages==int(raw_xml['metadata']['xmpTPg:NPages']) : #check if it worked correctly
         for i in range(num_pages):
           new.write(text_pages[i])
           new.write(" \n page_ended \n ") 
        os.remove(str(fp))
        filename = secure_filename(ok.filename)
        ok.save(os.path.join("PDF/", filename))
        return render_template('dashboard.html',current_user=current_user)

@app.route("/upload")
@login_required
def upload():
    return render_template("upload.html",current_user=current_user)

@app.route("/analyse")
@login_required
def analyse():
    return render_template("analyse.html",current_user=current_user)

@app.route("/wordcloud")
@login_required
def wordcloud():
    return render_template("wordcloud.html",current_user=current_user)

@app.route("/summarization")
@login_required
def summarization():
    return render_template("summarization.html",current_user=current_user)

@app.route("/qna")
@login_required
def qna():
    return render_template("qna.html",current_user=current_user)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html",current_user=current_user)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True,use_reloader=True)
