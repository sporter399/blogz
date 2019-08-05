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

   

@app.route('/allblogs', methods=['POST', 'GET'])
def all_blogs():

    blogs = db.session.query(Blog).all()
    
    counter = 1
    all_blogs = []
    for objects in blogs:
      blog = Blog.query.filter_by(id=counter).first()
      counter += 1
      all_blogs.append(blog)
    
    
    return render_template('allblogs.html',all_blogs=all_blogs)
  

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'display']
    if request.endpoint not in allowed_routes and 'user_name' not in session:
        return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():


      if request.method == 'POST':
          
          user_name = request.form['user_name']
          password = request.form['password']
          verify = request.form['verify']
          user_name_db_count = User.query.filter_by(user_name=user_name).count()
          if user_name_db_count > 0:
              flash('yikes! "' + user_name + '" is already taken and password reminders are not implemented')
              return redirect('/signup')
          if password != verify:
              flash('passwords did not match and this is flexblogz')
              return redirect('/signup')
          if (len(user_name) < 3) or (user_name.strip() == ""):
              flash("User names must contain at least 3 characters.")
              return redirect('/signup')
        
          if (len(password) <= 3) or (password.strip() == ""):
              flash("Passwords must contain at least 3 characters.")
              return redirect('/signup')
        
          user = User(user_name, password)
          db.session.add(user)
          db.session.commit()
          session['user_name'] = user_name
          
          return redirect("/test")
      
      else:
            return render_template('signup.html')
      

@app.route('/login', methods=['POST', 'GET'])
def login():
    
      
      if request.method == 'POST':
          
          
          user_name = request.form['user_name']
          password = request.form['password']
          existing_user = User.query.filter_by(user_name=user_name).first()
          
          if not existing_user:
              
              flash('Please register for an account to begin blogging.')
              
              return redirect('/signup')
      
          if not existing_user.password:
              flash('Password does not match')
              return redirect('/login')
          if existing_user and existing_user.password == password:
              session['user_name'] = user_name
              
              flash("Logged in")
              return redirect('/test')

         
       
      return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():

    del session['user_name']
    return redirect("/")



@app.route('/test', methods=['POST', 'GET'])
def test():

     

        return render_template('blogenter.html',title="Title for your new blog:", blog="Your blog")       

@app.route('/addconfirm', methods=['POST', 'GET'])
def addconfirm():

      owner = User.query.filter_by(user_name=session['user_name']).first()
      
      if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        owner_user_name = owner.user_name
        
        new_blog_object = Blog(title, blog, owner)
        db.session.add(new_blog_object)      
        db.session.commit()
        user_id = owner.id

      return render_template('addconfirm.html', title=title, blog=blog, 
      owner_user_name=owner_user_name, user_id=user_id, new_blog_object=new_blog_object)       

@app.route('/blogdisplay/<int:post_id>', methods=['POST', 'GET'])
def blog_display(post_id):

      display_list = []

      displayed_blog_object = Blog.query.filter_by(id=post_id).first()
      user_id = displayed_blog_object.owner_id
      user_filter = User.query.filter_by(id=user_id).first()
      returned_name = user_filter.user_name
      display_list.append(displayed_blog_object)

      return render_template('blogdisplay.html', display_list=display_list, 
      returned_name=returned_name, user_id=user_id)




@app.route('/display/<int:user_id>', methods=['POST', 'GET'])
def display(user_id):

      owner = User.query.filter_by(id=user_id).first()
      owner_user_name = owner.user_name   
      users_blogs = Blog.query.filter_by(owner_id=user_id).all()
            
      return render_template('userbloglist.html', users_blogs=users_blogs, user_id=user_id, owner_user_name=owner_user_name)




@app.route('/', methods=['POST', 'GET'])
def index():

    users = db.session.query(User).all()
    
    counter = 1
    all_users = []
    for objects in users:
      user = User.query.filter_by(id=counter).first()
      counter += 1
      all_users.append(user)
    
    
    return render_template('blog.html',all_users=all_users)
  



if __name__ == '__main__':
    app.run()
