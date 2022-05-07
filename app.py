from flask import Flask, redirect, render_template, request, session
from random import randint
import psycopg2
import bcrypt
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=recipe_box')
SECRET_KEY = os.environ.get('SECRET KEY', 'pretend secret key for testing')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_results')
def search_results():
    search_query = request.args.get('recipe')
    db_query = "%"+search_query+"%"

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url FROM recipes WHERE name LIKE %s', [db_query])
    results = cur.fetchall()
    conn.close()

    if not results: 
        return render_template('search_results.html', message='No results')
    else:
        return render_template('search_results.html', results=results)

@app.route('/randomise')
def randomiser():
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, ingredients, method FROM recipes ORDER BY random() LIMIT 1')

    results = cur.fetchall()
    print(results)
    conn.close()

    for result in results:
        name = result[0]
        ingredients = result[1]
        method = result[2]

    return render_template('recipe_page.html', recipe_name=name, recipe_ingredients=ingredients, recipe_method=method)

@app.route('/recipe_index')
def recipe_index():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url FROM recipes')
    returned = cur.fetchall()
    results = sorted(returned)
    conn.close()
    return render_template('recipe_index.html', results=results)

@app.route('/recipe_page/<name>')
def recipe_page(name):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url, ingredients, method FROM recipes WHERE name = %s', [name])
    results = cur.fetchall()
    conn.close()
    
    for result in results:
        name = result[0]
        image = result[1]
        ingredients = result[2]
        method = result[3]

    return render_template('recipe_page.html', recipe_name=name, recipe_image=image, recipe_ingredients=ingredients, recipe_method=method)

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

@app.route('/create_account_action', methods=['POST'])
def create_account_action():
    email = request.form.get('email')
    first_name = request.form.get('first-name')
    last_name = request.form.get('surname')
    password = request.form.get('password')
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('INSERT INTO users (email, first_name, last_name, password_hash) VALUES (%s, %s, %s, %s)', [email, first_name, last_name, password_hash])
    conn.commit()
    conn.close()
    def login(email):
        email = request.form.get('email')
        password = request.form.get('password')
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email = %s', [email])
        results = cur.fetchall()
        conn.close()

        password_hash = results[0][4]
        valid = bcrypt.checkpw(password.encode(), password_hash.encode())
        user_name = results[0][2]
        
        session['email'] = email
        session['name'] = user_name
    login(email)

    return redirect('/profile')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_action():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [email])
    results = cur.fetchall()
    conn.close()

    if not results:
        return render_template('login.html', message='User not found')
    else:
        password_hash = results[0][4]
        valid = bcrypt.checkpw(password.encode(), password_hash.encode())
        if valid:
            user_name = results[0][2]
            user_id = results[0][0]
            session['email'] = email
            session['name'] = user_name
            session['id'] = user_id

            return redirect('/')
        else:
            print('invalid')
            return render_template('login.html', message='User not found')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    email = session['email']
    name = session['name']
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url, user_id, recipes.id, email FROM recipes JOIN users ON recipes.user_id = users.id')
    results = cur.fetchall()
    conn.close()
    return render_template('profile.html', email=email, name=name, results=results)

@app.route('/delete_recipe/<name>')
def delete_recipe(name):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM recipes WHERE name = %s', [name])
    results = cur.fetchall()
    
    for result in results:
        recipe_id = result[0]
        recipe_name = result[1]
    conn.close()
    return render_template('delete_recipe.html', name=recipe_name, id=recipe_id)

@app.route('/delete_recipe_action', methods=['POST'])
def delete_recipe_action():
    id = request.form.get('id')

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('DELETE FROM recipes WHERE (id) = (%s)', [id])

    conn.commit()
    conn.close()
    return redirect('/profile')

@app.route('/add_recipe')
def add_recipe():
    return render_template('add_recipe.html')

@app.route('/add_recipe_action', methods=['POST'])
def add_recipe_action():
    name = request.form.get('name')
    print(name)
    image_url = request.form.get('image_url')
    method = request.form.get('method')
    ingredients = request.form.get('ingredients')

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('INSERT INTO recipes (name, image_url, method, ingredients) VALUES (%s, %s, %s, %s)', [name, image_url, method, ingredients])

    sess_id = str(session['id'])
    print(sess_id)
    user_id = sess_id
    print(user_id)

    query = """UPDATE recipes SET user_id = %s WHERE name = %s"""
    tuple1 = (user_id, name)
    cur.execute(query, tuple1)

    conn.commit()
    conn.close()

    return redirect('/profile')

if __name__ == "__main__":
    app.run(debug=True)