import sqlite3

# יצירת חיבור למסד הנתונים
conn = sqlite3.connect('garage.db')
cursor = conn.cursor()

# יצירת טבלת מכוניות
cursor.execute('''
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT UNIQUE NOT NULL,
    image TEXT NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0
)
''')

# בדיקה אם העמודה 'deleted' קיימת והוספתה אם היא לא קיימת
cursor.execute("PRAGMA table_info(cars)")
columns = [column[1] for column in cursor.fetchall()]
if 'deleted' not in columns:
    cursor.execute("ALTER TABLE cars ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT 0")

# הוספת נתונים לטבלת מכוניות
cars_data = [
    ('123ABC', 'https://shaul-wallpaper.co.il/wp-content/uploads/cloud/2233.jpg'),
    ('456DEF', 'https://sc01.alicdn.com/kf/HTB1zN7lJ7KWBuNjy1zjq6AOypXa1/Rastar-Lamborghini-Remote-Control-Rc-Car-1.jpg'),
    ('789GHI', 'https://union-motors.toyota.co.il/public-images/cars/CorollaSedan.png')
]

cursor.executemany('INSERT OR IGNORE INTO cars (number, image) VALUES (?, ?)', cars_data)

# יצירת טבלת בעיות
cursor.execute('''
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_name TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL
)
''')

# הוספת נתונים לטבלת בעיות
problems_data = [
    ('Flat Tire', 50.00),
    ('Oil Change', 30.00),
    ('Brake Repair', 100.00)
]

cursor.executemany('INSERT OR IGNORE INTO problems (problem_name, amount) VALUES (?, ?)', problems_data)

# יצירת טבלת קישור בין מכוניות לבעיות
cursor.execute('''
CREATE TABLE IF NOT EXISTS car_problems (
    car_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    FOREIGN KEY (car_id) REFERENCES cars(id),
    FOREIGN KEY (problem_id) REFERENCES problems(id),
    PRIMARY KEY (car_id, problem_id)
)
''')

# שמירת השינויים וסגירת החיבור
conn.commit()
conn.close()
