from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3

app = Flask(__name__)

app.config['DEBUG'] = True
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "blogz.db"))
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    
    def __init__(self, title, blog, owner):
       self.title = title
       self.blog = blog
       self.owner = owner


@app.route('/signup', methods=['POST', 'GET'])
def signup():


      """
      it does not appear that database is actually alquiring and storing info. 
      the code executes to the next page after signup button as defined in the html
      to blog entry page, but username of user is not "following" the navigation 
      and thus fails in add confirm
      """
      print("this is before post request method")
      if request.method == 'POST':
          print("does post request method execute?")
          user_name = request.form['user_name']
          password = request.form['password']
          verify = request.form['verify']
          user_name_db_count = User.query.filter_by(user_name=user_name).count()
          if user_name_db_count > 0:
              flash('yikes! "' + user_name + '" is already taken and password reminders are not implemented')
              return redirect('/signup')
          if password != verify:
              flash('passwords did not match')
              return redirect('/signup')
          if (len(user_name) <= 3) or (user_name.strip() == ""):
              flash("User names must contain at least 3 characters.")
              return redirect('/signup')
        
          if (len(password) <= 3) or (password.strip() == ""):
              flash("Passwords must contain at least 3 characters.")
              return redirect('/signup')
        
          user = User(user_name=user_name, password=password)
          db.session.add(user, password)
          db.session.commit()
          session['user_name'] = user.user_name
          print("this is user" +  str(user))
          return redirect("/test")
      
      else:
            return render_template('signup.html')
      

@app.route('/login', methods=['POST', 'GET'])
def login():

      if request.method == 'POST':
          print("alphaexecute")
          user_name = request.form['user_name']
          password = request.form['password']
          user = User.query.filter_by(user_name=user_name).first()

          if user_name != user:
              flash('Please register for an account to begin blogging.')
              return redirect('/signup')
      
          if password != password:
              flash('Passwords do not match')
              return redirect('/signup')
            
          if user and user.password == password:
              session['user_name'] = user_name
              flash("Logged in")
              
              return redirect('/addconfirm', user_name=user_name, password=password)
       
      return render_template('login.html')
"""
@app.route('/', methods=['POST', 'GET'])
def index():

      return
"""

@app.route('/logout', methods=['POST', 'GET'])
def logout():

      return redirect('/blog.html')



@app.route('/test', methods=['POST', 'GET'])
def test():

      
     
      return render_template('blogenter.html',title="Title for your new blog:", blog="Your blog")       

@app.route('/addconfirm', methods=['POST', 'GET'])
def addconfirm():
      
      #app must acquire identity of a logged in user here as they enter their blog
      #code below might be failing because db is not acquiring anything
      owner = User.query.filter_by(user_name=session['user_name']).first()
      
      if request.method == 'POST':
       
        title = request.form['title']
        blog = request.form['blog'] 
        new_blog_object = Blog(title, blog, owner)
        db.session.add(new_blog_object)      
        db.session.commit()

      return render_template('addconfirm.html', new_blog_object=new_blog_object)       

@app.route('/display/<int:post_id>', methods=['POST', 'GET'])
def display(post_id):

      display_list = []

      displayed_blog_object = Blog.query.filter_by(id=post_id).first()
      display_list.append(displayed_blog_object)
     
      return render_template('blogdisplay.html', display_list=display_list)


@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = db.session.query(Blog).all()
    
    counter = 1
    loop_queries = []
    for objects in blogs:
      loop_query = Blog.query.filter_by(id=counter).first()
      counter += 1
      loop_queries.append(loop_query)
    
    
    return render_template('blog.html',loop_queries=loop_queries)
  



if __name__ == '__main__':
    app.run()
