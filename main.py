
from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from datetime import datetime
import json
import os
import math



with open("config.json","r") as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'the-random-string'
app.config['UPLOAD_FOLDER'] = params["upload_location"]


# uri
local_server = True
if (local_server == True):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)


# mysql://username:password@server/db




class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    phone_num = db.Column(db.String(120), unique=True)
    date = db.Column(db.String(120),nullable = True,unique=False)
    email = db.Column(db.String(120), unique=True)
    messege = db.Column(db.String(120), unique=True)



class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    img_file = db.Column(db.String(120), unique=True)
    subtitle = db.Column(db.String(120), unique=False)
    slug = db.Column(db.String(120), unique=True)
    content = db.Column(db.String(120), unique=True)
    date = db.Column(db.String(120), unique=False)

    



@app.route("/")
def Home():
    post = Post.query.filter_by().all()
    last = math.ceil(len(post)/int(params["no_of_post"]))
    # [0:params["no_of_post"]]

    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page-1)*int(params["no_of_post"]):(page-1)*int(params["no_of_post"])+int(params["no_of_post"])]
    # pagination logic
    # first:
    if (page==1):
        prev = "#"
        next = '/?page='+str(page+1)
    
    elif (page==last):
        prev = '/?page='+str(page-1)
        next = "#"
    else:
        prev = '/?page='+str(page-1)
        next = '/?page='+str(page+1)

    
    return render_template("index.html",params = params,post = post,prev = prev,next = next)


@app.route("/about")
def about():
    return render_template("about.html")

# gaining data from database for frontend template
@app.route("/post/<string:post_slug>",methods = ['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug = post_slug).first()
    return render_template("post.html",post = post,params = params,)




'''post(template passing variable) = post (data of variable that value data pass in templates)'''

# ------------------------------------------------------

""" database connect...
 transfer template data in database..."""


@app.route("/contact",methods = ['GET','POST'])
def contact():
    if (request.method =='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        messege = request.form.get('messege')
        entry = Contacts(name = name , email = email , phone_num = phone,date= datetime.now(),messege = messege)
        db.session.add(entry)
        db.session.commit()
    return render_template("contact.html")


# login page------------------------------>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():
    if ("user" in session and session['user'] == params["admin_user"]):
        posts = Post.query.all()
        return render_template("dashboard.html",posts = posts)




    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("pass")
        if username == params["admin_user"] and password == params["admin_pass"]:
            session['user'] = username
            posts = Post.query.all()
            return render_template('dashboard.html',params = params,posts = posts)
        return render_template("login.html",params = params)  
    else:
        return render_template("login.html",params = params)   



# add a new post
@app.route("/edit/<string:sno>",methods = ['GET','POST'])
def edit(sno):
    if ("user" in session and session['user'] == params["admin_user"]):
        if request.method == "POST":
            title = request.form.get("title")
            img_file = request.form.get("img_file")
            subtitle = request.form.get("subtitle")
            slug = request.form.get("slug")
            content = request.form.get("content")
            date = datetime.now()
            
            if sno == "0":
                post = Post(title = title,subtitle = subtitle,img_file = img_file,slug = slug , content = content,date = date)
                db.session.add(post)
                db.session.commit()
                
                
            else:
                post = Post.query.filter_by(sno = sno).first()
                post.title = title
                post.subtitle = subtitle
                post.img_file = img_file
                post.slug = slug
                post.content = content
                post.date = date
                db.session.commit()
                return redirect("/edit/" + sno)    
    post = Post.query.filter_by(sno = sno).first()
    return render_template('edit.html',params=params,sno = sno,post = post)


# file uploader


@app.route("/uploader",methods = ['GET','POST'])
def uploader():
    if ("user" in session and session['user'] == params["admin_user"]):
        if (request.method == "POST"):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return " UPLOADED SUCCESSFULLY"



# logout


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

# delete post

@app.route("/delete/<string:sno>",methods = ['GET','POST'])
def delete(sno):
    if ("user" in session and session['user'] == params["admin_user"]):
        post = Post.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')





if __name__ == "__main__":
    app.run(debug=True)