import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    
    # update DB connection counter every time we communicate with the DB
    connection.execute('UPDATE dbConnections SET db_connection_count = db_connection_count + 1 WHERE id = 1')
    connection.commit()
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("No article found with id '{}'".format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info('Article {}'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The 'About Us' page is retrieved.")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            connection.commit()
            connection.close()
            app.logger.info("A new article is created with title {}".format(title))
        
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json')
    
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    db_connection = connection.execute('SELECT db_connection_count FROM dbConnections WHERE id = 1').fetchone()
    db_connection_count = db_connection['db_connection_count']
    connection.close()
    response = app.response_class(
        response = json.dumps(
            {
                "db_connection_count":db_connection_count,
                "post_count": len(posts)
            }),
        status=200,
		mimetype='application/json'
    )
    
    return response

if __name__ == "__main__":
    # set logger to handle STDOUT and STDERR 
    stderr_handler = logging.StreamHandler() # default stream -> stderr
    stderr_handler.setLevel(logging.ERROR)
    
    stdout_handler = logging.FileHandler('app.log')
    stdout_handler.setLevel(logging.DEBUG)
    handlers = [stdout_handler, stderr_handler]
 
    # format output
    format_output = '%(asctime)s %(levelname)-8s %(message)s'

    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers, datefmt='%Y-%m-%d %H:%M:%S')
    # start the application on port 3111
    app.run(host='0.0.0.0', port='3111')