from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey, String, Column
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Life1988@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'God'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    #owner_id = db.Column(db.Integer, foreign_key('User'))
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, owner, title, body):
        self.owner = owner
        self.title = title
        self.body = body

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(20))
    #blogs = db.Column(db.Text)
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        #self.blogs = blogs

allowed_routes = ['login', 'signup', 'index', 'blog', 'static', 'singleUser']


@app.before_request
def req_login():
    
    if not (request.endpoint in allowed_routes or 'username' in session):
        return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_pw = request.form['verify_pw']
        user = User.query.filter_by(username=username).first()

        username_error=''
        password_error=''
        verify_pw_error=''

        #add new user to database
        if not user and len(password) > 3 and password == verify_pw:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        #verify username
        if username == '' or password == '' or verify_pw == '':
            flash ('Your Username and/or Password is invalid')
            username_error = False
            password_error = False
            verify_pw_error = False

        if username == '':
            username_error = False
            username = ''
            flash('Your username should be between 5 and 20 characters.')

        elif len(username) < 3:
            username_error = False
            username = ''
            flash('Your username should be between 5 and 20 characters.')

        elif existing_user:
            username_error = False
            username = ''
            flash('The username your are trying to use it already taken - Please try again.')

        #verify Passwords
        if password == '':
            password_error = False
            password = ''
            flash('Please enter password')

        elif len(password) < 5:
            password_error = False
            password = ''
            flash('Your password should be between 5 and 20 characters.')

        elif password != verify_pw:
            password_error = False
            password = ''
            flash('Your passwords do not match - Please try again.')

        return render_template('/newpost.html', username=username, username_error=username_error, password_error=password_error, verify_pw_error=verify_pw_error)

    return render_template("/signup.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""

        if user and user.password == password:
            session['username'] = username
            flash('You are logged in!')
            return redirect('/newpost')

        elif user == '':
            username_error = False
            username = ''
            flash('Username is not filled - Try again.')


        elif not user:
            username_error = True
            username = ''
            flash ('Username does not exist')


        if password == "":
            password_error = False
            password = ''
            flash('Your password does not match - Try again')

        return render_template("login.html", username=username, username_error=username_error, password_error=password_error)

    return render_template("login.html")


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)

@app.route('/singleuser', methods=['GET'])
def showuser():
    user_id = request.args.get('user')
    user = User.query.filter_by(id=user_id).first()
    blogs = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('singleuser.html', user=user, blogs=blogs)



# TODO: redirected from / showing all blogs
@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get('id')

    if blog_id == None:
        posts = Blog.query.all()
        return render_template('blog.html', blogs=posts, title='blogz')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

### TODO: query all blogs and return/gets the selected blog
@app.route('/selected_blog', methods=['GET'])
def selected_blog():
    blog_id = request.args.get('id')
    blog_post = Blogz.query.get(blog_id)
    owner_id = blog_post.owner_id
    user = User.query.get(owner_id)
    return render_template('selected_blog.html', user_id=blog_id, blog=blog_post, user=owner_id, username=user)




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        username = session['username']
        title_error = ''
        body_error = ''

        if blog_title == None:
            title_error = "Please enter a blog title"
            print(title_error)
        if not blog_body:
            body_error = "Please enter a blog entry"
            print(body_error)

        if not body_error and not title_error:
            new_entry = Blog(logged_in_user(username), blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    return render_template('newpost.html', title='New Entry')

def logged_in_user(username):
    user = User.query.filter_by(username= username).first()
    return user
    

if __name__ == '__main__':
    app.run()