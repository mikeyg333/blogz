from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def index():
    
    blog_id = request.args.get('id')
    
    if not blog_id:
        
        blogs = Blog.query.all()
            
        return render_template('entries.html', title="Build A Blog!",
            blogs=blogs)
        
    else:
        
        blog_id_int = int(blog_id)
        specific_blog = Blog.query.get(blog_id_int)
        blog_title = specific_blog.title
        blog_body = specific_blog.body
            
        return render_template('individual.html', blog_title=blog_title, blog_body=blog_body)
    
@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ''
        body_error = ''

        if not blog_title:
            
            title_error = 'Please fill in the blog title'

        if not blog_body:
            
            body_error = 'Please fill in the blog body'
        
        if not title_error and not body_error:
            
            new_entry = Blog(blog_title, blog_body)
            db.session.add(new_entry)
            db.session.commit()

            id = str(new_entry.id)
            
            return redirect('/blog?id=' + id)

        else:
            
            return render_template('form.html', blog_title=blog_title,
                title_error=title_error, blog_body=blog_body,
                body_error=body_error)
    
    return render_template('form.html')

if __name__ == '__main__':
    app.run()