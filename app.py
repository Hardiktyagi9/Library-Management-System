import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import MySQLdb

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Temporary configuration to connect to MySQL server without a specific database
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = ''  # Initially empty to avoid "unknown database" error

mysql = MySQL(app)

def setup_database():
    try:
        # Establish a raw connection without specifying a database
        conn = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD')
        )
        cursor = conn.cursor()
        
        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
        conn.commit()
        
        # Re-configure the app to use the `library_db` database now that it exists
        app.config['MYSQL_DB'] = 'library_db'
        mysql.init_app(app)  # Reinitialize MySQL with the new database config
        
        # Now create the `books` table if it doesn't exist
        conn.select_db('library_db')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100)
            )
        """)
        conn.commit()
        
        cursor.close()
        conn.close()
        print("Database 'library_db' and table 'books' created successfully.")
    except Exception as e:
        print(f"Error during database setup: {e}")

@app.route('/')
def index():
    setup_database()  # Ensure the database and table exist
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    cur.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)", 
            (title, author, genre))
        
        mysql.connection.commit()
        cur.close()
        flash("Book added successfully!")
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Book deleted successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)