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
    cur.execute('SELECT name, image_url FROM recipes WHERE name = %s', [name])
    results = cur.fetchall()
    conn.close()
    
    for result in results:
        recipe = result[0]
        image = result[1]
        print(result)

    recipe_name = recipe
    return render_template('recipe_page.html', recipe_name=recipe, recipe_image=image )

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_action():
    email = request.form.get('email')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT email, first_name FROM users')
    results = cur.fetchall()
    users = {}
    conn.close()

    for result in results:
        users[result[0]] = result[1]

    if email in users:
        print(f'success {email}')
        session['email'] = email
        return redirect('/')   
    else:
        print('invalid')
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/add_recipe')
def add_recipe():
    return render_template('add_food.html')

@app.route('/add_recipe_action', methods=['POST'])
def add_recipe_action():
  name = request.form.get('name')
  image_url = request.form.get('image_url')
  price = request.form.get('price')

  conn = psycopg2.connect('dbname=foodtruck')
  cur = conn.cursor()
  cur.execute('INSERT INTO food (name, image_url, price_in_cents) VALUES (%s, %s, %s)', [name, image_url, price])

  conn.commit()
  conn.close()
  return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)