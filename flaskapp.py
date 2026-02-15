from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from flask import send_from_directory

UPLOAD_FOLDER = '/var/www/flask_app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    
    conn = sqlite3.connect('/var/www/flask_app/users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
              (username, password, firstname, lastname, email))
    conn.commit()
    conn.close()
    
    return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect('/var/www/flask_app/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('/var/www/flask_app/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return redirect(url_for('profile', username=username))
    else:
        return "Invalid username or password. Please go back and try again."

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    username = request.form['username']
    
    if file:
        filename = 'Limerick.txt'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Count words
        with open(filepath, 'r') as f:
            content = f.read()
            word_count = len(content.split())

        # Get user info
        conn = sqlite3.connect('/var/www/flask_app/users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        return render_template('profile.html', user=user, word_count=word_count)
    return "No file uploaded"

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
