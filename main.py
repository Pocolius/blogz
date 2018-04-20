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
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.args.get('id'):
        id = request.args.get('id')
        blog = Blog.query.filter_by(id=id).first()
        return render_template('singleblog.html', title="Build-A-Blog", blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build-A-Blog", blogs=blogs)

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
    allowed_routes = ['login', 'signup']
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
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():

    author = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['body']
        new_post = Blog(blog_title, blog_content, author)
        db.session.add(new_post)
        db.session.commit()

    blogs = Blog.query.filter_by(author=author).all()
    return render_template('blog.html',title="Blogz", 
        blogs=blogs)

if __name__ == '__main__':
    app.run()