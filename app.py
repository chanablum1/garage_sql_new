from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# פונקציה לחיבור למסד הנתונים
def get_db_connection():
    conn = sqlite3.connect('garage.db')
    conn.row_factory = sqlite3.Row
    return conn

# יצירת טבלאות אם לא קיימות
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT UNIQUE NOT NULL,
        image TEXT NOT NULL,
        deleted BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    cursor.execute("PRAGMA table_info(cars)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'deleted' not in columns:
        cursor.execute("ALTER TABLE cars ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT 0")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_name TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS car_problems (
        car_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        FOREIGN KEY (car_id) REFERENCES cars(id),
        FOREIGN KEY (problem_id) REFERENCES problems(id),
        PRIMARY KEY (car_id, problem_id)
    )
    ''')
    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars WHERE deleted = 0').fetchall()
    conn.close()
    return render_template('index.html', cars=cars)

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        number = request.form['number']
        image = request.form['image']
        conn = get_db_connection()
        conn.execute('INSERT INTO cars (number, image) VALUES (?, ?)', (number, image))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_car.html')

@app.route('/delete_car/<int:id>', methods=['POST'])
def delete_car(id):
    conn = get_db_connection()
    conn.execute('UPDATE cars SET deleted = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_car/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        number = request.form['number']
        image = request.form['image']
        conn.execute('UPDATE cars SET number = ?, image = ? WHERE id = ?', (number, image, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('edit_car.html', car=car)

@app.route('/car/<int:id>', methods=['GET', 'POST'])
def car_details(id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
    problems = conn.execute('SELECT * FROM problems').fetchall()
    car_problems = conn.execute('SELECT problem_id FROM car_problems WHERE car_id = ?', (id,)).fetchall()
    car_problems_ids = [problem['problem_id'] for problem in car_problems]
    
    if request.method == 'POST':
        selected_problems = request.form.getlist('problems')
        conn.execute('DELETE FROM car_problems WHERE car_id = ?', (id,))
        for problem_id in selected_problems:
            conn.execute('INSERT INTO car_problems (car_id, problem_id) VALUES (?, ?)', (id, problem_id))
        conn.commit()
        conn.close()
        return redirect(url_for('car_details', id=id))

    conn.close()
    return render_template('car_details.html', car=car, problems=problems, car_problems_ids=car_problems_ids)

if __name__ == "__main__":
    app.run(debug=True)
