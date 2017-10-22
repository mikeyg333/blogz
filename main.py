from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'blogz'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog_list', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            if not user:
                flash('Username does not exist', 'error')
            if user and user.password != password:
                flash('Password is incorrect, please enter correct password', 'error')
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and username != "" and password != "" and verify != "" and password == verify and len(username) > 2 and len(password) > 2:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            if not username or not password or not verify:
                flash('One or more fields are blank', 'error')
            if existing_user:
                flash('Username already exists', 'error')
            if password != verify:
                flash('Password do not match', 'error')
            if len(username) < 3:
                flash('Invalid username, must be 3 characters or more', 'error')
            if len(password) < 3:
                flash('Invalid password, must be 3 characters or more', 'error')
        
    return render_template('/signup.html')

@app.route('/blog')
def blog_list():
    
    blog_id = request.args.get('blog_id')
    individual_user = request.args.get('user')
    blogs = Blog.query.all()

    if not blog_id and not individual_user:
        
        return render_template('all_entries.html', title="Build A Blog!",
            blogs=blogs)
        
    elif blog_id:
        
        blog_id_int = int(blog_id)
        specific_blog = Blog.query.get(blog_id_int)
            
        return render_template('individual_blog.html', specific_blog=specific_blog)
    
    elif individual_user:

        return render_template('individual_user.html', individual_user=individual_user, blogs=blogs)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        title_error = ''
        body_error = ''

        if not blog_title:
            
            title_error = 'Please fill in the blog title'

        if not blog_body:
            
            body_error = 'Please fill in the blog body'
        
        if not title_error and not body_error:
            
            new_entry = Blog(blog_title, blog_body, owner)
            db.session.add(new_entry)
            db.session.commit()

            blog_id = str(new_entry.id)
            
            return redirect('/blog?blog_id=' + blog_id)

        else:
            
            return render_template('form.html', blog_title=blog_title,
                title_error=title_error, blog_body=blog_body,
                body_error=body_error)
    
    return render_template('form.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()