#TODO List
#add the following templates: signup.html, login.html, index.html
#add a singleUser.html template - will display blogs only by a single author
#add route handler functions for signup, login, and index
#add a logout function that handles a POST request to /logout and
#redirects to /blog after deleting the user from the session
#add a User class

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#TODO - verify constructor objects are accurate as well as foreign key setup
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#TODO - verify blogs relationship works properly as well as maybe constructor?
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner_id')

    def __init__(self, username, password, blogs):
        self.uesrname = username
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
        #something here for user
        error = ''

        if blog_content == '' or blog_title == '':
            error = "Whoops! You're missing something. Please make sure you have a title and some content."

        if error != '':
            return render_template('newpost.html', title="Build-A-Blog", 
            blog_title=blog_title, blog_content=blog_content, error=error)

        else:
            new_blog = Blog(blog_title, blog_content)
            db.session.add(new_blog)
            db.session.commit()

            recent_post = Blog.query.filter_by(title=blog_title).first()
            id = recent_post.id
            blog = Blog.query.filter_by(id=id).first()
            return redirect("/blog?id=" + str(id))

    else:
        return render_template('newpost.html', title="Build-A-Blog - New Post")

if __name__ == '__main__':
    app.run()