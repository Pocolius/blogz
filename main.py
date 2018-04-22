#TODO List
#add the following templates: signup.html, login.html, index.html
#add a singleUser.html template - will display blogs only by a single author
#add route handler functions for signup, login, and index
#add a logout function that handles a POST request to /logout and
#redirects to /blog after deleting the user from the session
#add a User class

from flask import Flask, flash, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#TODO - verify constructor objects are accurate as well as foreign key setup
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

#TODO - verify blogs relationship works properly as well as maybe constructor?
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['body']
        author = User.query.filter_by(username=session['username']).first()
        new_post = Blog(blog_title, blog_content, author)
        db.session.add(new_post)
        db.session.commit()

    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.filter_by(id=id).first()
        return render_template('singleblog.html', title="Build-A-Blog", blog=blog)

    if request.args.get('user'):
        user = request.args.get('user')
        user_posts = Blog.query.filter_by(owner_id=user).all()
        return render_template('blog.html', title="Blogz", blogs=user_posts)

    else:
        blogs = Blog.query.all()
        username = request.args.get('user')
        user = User.query.filter_by(username=username).all()
        return render_template('blog.html', title="Build-A-Blog", blogs=blogs, user=user)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['body']
        blog_author = User.query.filter_by(username=session['username']).first()
        error = ''

        if blog_content == '' or blog_title == '':
            error = "Whoops! You're missing something. Please make sure you have a title and some content."

        if error != '':
            return render_template('newpost.html', title="Build-A-Blog", 
            blog_title=blog_title, blog_content=blog_content, error=error)

        else:
            new_blog = Blog(blog_title, blog_content, blog_author)
            db.session.add(new_blog)
            db.session.commit()

            recent_post = Blog.query.filter_by(body=blog_content).first()
            id = recent_post.id
            blog = Blog.query.filter_by(id=id).first()
            return redirect("/blog?id=" + str(id))

    else:
        return render_template('newpost.html', title="Build-A-Blog - New Post")

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('Your username or password is incorrect. Please try again.', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username_error = ''
    password_error = ''
    v_password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        v_password = request.form['verify']

        if username == '':
            username_error = 'Please enter a Username.'
        if len(username) < 3 or len(username) > 20:
            username_error = 'Your username must be more than 3 characters and less than 20 characters.'
        if ' ' in username:
            username_error = 'Your username cannot contain any spaces.'

        if password == '':
            password_error = 'Please enter a password.'
        if len(password) < 3 or len(password) > 40:
            password_error = 'Your password must be more than 3 characters and less than 40 characters.'
        if ' ' in password:
            password_error = 'Your password cannot contain any spaces.'

        if v_password == '':
            v_password_error = 'Please re-enter your password.'

        if password != v_password:
            password_error = ''
            v_password_error = 'Please verify with a correct password.'

        if username_error != '' or password_error != '' or v_password_error != '':
                return render_template('signup.html', username_error=username_error, password_error=password_error, 
                v_password_error=v_password_error)

        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = 'This username is already taken.'

    return render_template('signup.html', username_error=username_error, password_error=password_error, 
                v_password_error=v_password_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title="Blogz", users=users)

if __name__ == '__main__':
    app.run()