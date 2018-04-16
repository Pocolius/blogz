from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# TODO
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#####################START CHANGES HERE#####################

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_content = request.form['body']
        new_blog = Blog(blog_title, blog_content)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build-A-Blog", blogs=blogs)


#@app.route('/delete-task', methods=['POST'])
#def delete_task():

#    task_id = int(request.form['task-id'])
#    task = Task.query.get(task_id)
#    task.completed = True
#    db.session.add(task)
#    db.session.commit()

#    return redirect('/')


###################STOP CHANGES HERE#################

if __name__ == '__main__':
    app.run()