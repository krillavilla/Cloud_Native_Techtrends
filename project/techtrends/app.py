import sqlite3
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash, g
from werkzeug.exceptions import abort
import logging

# Function to get a database connection
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    if 'db_connection_count' not in g:
        g.db_connection_count = 0
    g.db_connection_count += 1

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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')
formatter = logging.Formatter('%(asctime)s, %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

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
        logger.info(f'A non-existing article with id {post_id} is accessed and a 404 page is returned.')
        return render_template('404.html'), 404
    else:
        logger.info(f'Article "{post["title"]}" retrieved.')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About Us page retrieved.')
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
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            logger.info(f'New article "{title}" created.')
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the health check endpoint
@app.route('/healthz')
def health_check():
    return jsonify(result="OK - healthy"), 200

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    db_connection_count = g.get('db_connection_count', 0)

    return jsonify(db_connection_count=db_connection_count, post_count=post_count), 200

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3111)
