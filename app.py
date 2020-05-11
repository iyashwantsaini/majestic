import os
from flask import Flask, render_template,request

app = Flask(__name__)

@app.route("/")
def index():
        return render_template("login.html")



@app.route('/selection',methods=['POST','GET'])
def selection():
    
    username = request.form['username']
    password= request.form['password']
    
    if username=='thapar' and password=='thapar':
        return render_template('dashboard.html')
    else :
        return render_template('login.html', warning='Please enter correct username and password')

if __name__ == "__main__":
    app.run()
