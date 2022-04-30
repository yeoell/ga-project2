from flask import Flask, redirect, render_template, request, session
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=recipe_box')
SECRET_KEY = os.environ.get('SECRET KEY', 'pretend secret key for testing')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recipe_index')
def recipe_index():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url FROM recipes')
    returned = cur.fetchall()
    results = sorted(returned)
    print(results)
    conn.close()
    return render_template('recipe_index.html', results=results)

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)