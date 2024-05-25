
# You need to build a simple API that fetches data from a mock database and
# allows users to perform basic SQL queries on this data. The API should have
# the following functionalities:

# Fetch all records: Retrieve all records from a predefined table.
# Fetch a specific record: Retrieve a specific record based on a provided identifier.
# Run a custom SQL query: Allow users to run custom SQL queries on the data and return the results.

# GET /library
# GET /library/{book}
# POST /query

# Mock Database: SQLite (local)
# API: Build with Flask

# Database Schema
# - book: int
# - name: varchar(n)
# - checked_out: varchar(n)

# Table
# - 1 | Dr. Suess |
# - 2 | Harry Potter | Bob
# - 3 | Dr. Suess | Alice

# Initial DB with some records
# Records could be initialized from a .csv or just add in a few records with INSERT INTO

# Get Function

# Get Specific Record Function

# Run Query Function

from flask import Flask, jsonify, request
import sqlite3
from sqlite3 import Error


app = Flask(__name__)

# Initialize the in-memory database and create the employees table
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS lib')
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS lib (
                id INTEGER PRIMARY KEY,
                name TEXT,
                reader TEXT
            );
        '''
    )
    
    cursor.execute(
        '''
        INSERT INTO lib (id, name, reader) VALUES 
        (1, 'Dr. Seuss', ?),
        (2, 'Harry Potter', 'Alice'),
        (3, 'Dr. Seuss', 'Bob')               
        ''', ('',)
    )
                       
    conn.commit()


# Example:
# curl http://localhost:5000/library
@app.route('/library', methods=['GET'])
def get_catalog():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lib')
        rows = cursor.fetchall()
        return jsonify(rows)
    
# Example:
# curl http://localhost:5000/library/Dr.%20Seuss
@app.route('/library/<string:book>', methods=['GET'])
def get_books(book):
    print("Hello wrold!", flush=True)
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM lib WHERE name = ?', (book,))
        rows = cursor.fetchall()

        if rows:
            return jsonify(rows)
        else:
            return jsonify({'Key Error': f'Library does not contain {book}'}), 404
        
# Example:
# curl  -X POST \
#   'http://localhost:5000/query' \
#   --header 'Accept: */*' \
#   --header 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
#   --header 'Content-Type: application/json' \
#   --data-raw '{"query": "SELECT * FROM lib"}'
@app.route('/query', methods=['POST'])
def run_query():
    with sqlite3.connect('library.db') as conn:
        query = request.json['query']

        try:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return jsonify(rows), 200
        except Exception as e:
            return jsonify({'Error': str(e)}), 400
        
# Example:
# curl  -X POST \
#   'http://localhost:5000/library/add' \
#   --header 'Accept: */*' \
#   --header 'User-Agent: Thunder Client (https://www.thunderclient.com)' \
#   --header 'Content-Type: application/json' \
#   --data-raw '{"book": "Mistborn"}'
@app.route('/library/add', methods=["POST"])
def add_book():
    with sqlite3.connect('library.db') as conn:
        book_name = request.json["book"]

        try:
            cursor = conn.cursor()

            # Generate a new ID
            cursor.execute(
                '''
                SELECT max(id) FROM lib
                '''
            )

            row = cursor.fetchone()
            book_id = row[0] + 1

            cursor.execute('INSERT INTO lib VALUES (?, ?, ?)', (book_id, book_name, None))
            conn.commit()

            return jsonify({'Response': f'Successfully added {book_name} to the catalog'}), 200
        except Exception as e:
            return jsonify({'Error': str(e)}), 400


if __name__ == "__main__":
    init_db()
    app.run(debug=False)