from flask import Flask, redirect, render_template, request, session
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
    print(db_query)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT name, image_url FROM recipes WHERE name LIKE %s', [db_query])
    results = cur.fetchall()
    print(results)
    conn.close()

    if not results: 
        return render_template('search_results.html', results='no results')
    else:
        return render_template('search_results.html', results=results)

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
    cur.execute('SELECT name, image_url, ingredients, method FROM recipes JOIN recipe_detail ON recipes.id = recipe_detail.id WHERE name = %s', [name])
    results = cur.fetchall()
    conn.close()
    
    for result in results:
        name = result[0]
        image = result[1]
        ingredients = result[2]
        method = result[3]
        print(result)

    # recipe_name = name
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
    cur.execute('INSERT INTO users (email, first_name, last_name, password_hash) VALUES (%s, %s, %s, %s)', [email], [first_name], [last_name], [password_hash])
    # results = cur.fetchall()
    conn.close()

    return redirect('/login')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_action():
    email = request.form.get('email')
    password = request.form.get('password')
    print(f'{email} {password}')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s', [email])
    results = cur.fetchall()
    print(results)
    # users = {}
    conn.close()

    if not results:
        return render_template('login.html', message='User not found')
    else:
        password_hash = results[0][4]
        valid = bcrypt.checkpw(password.encode(), password_hash.encode())
        if valid:
            user_name = results[0][2]
            print(f'{user_name}, password valid')
            session['email'] = email
            session['name'] = user_name
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
    return render_template('profile.html', email=email, name=name)

@app.route('/add_recipe')
def add_recipe():
    return render_template('add_recipe.html')

# @app.route('/add_recipe_action', methods=['POST'])
# def add_recipe_action():
#   name = request.form.get('name')
#   image_url = request.form.get('image_url')
#   price = request.form.get('price')

#   conn = psycopg2.connect('dbname=foodtruck')
#   cur = conn.cursor()
# #   cur.execute('INSERT INTO food (name, image_url, price_in_cents) VALUES (%s, %s, %s)', [name, image_url, price])

#   conn.commit()
#   conn.close()
#   return redirect('/recipe_page/<name>')

if __name__ == "__main__":
    app.run(debug=True)