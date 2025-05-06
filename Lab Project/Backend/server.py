from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import check_password_hash
from flask_cors import CORS
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for local development

DATABASE = 'elibrary.db'

# Azure Language Service credentials
LANGUAGE_KEY = os.getenv('AZURE_LANGUAGE_KEY', 'your-key-here')
LANGUAGE_ENDPOINT = os.getenv('AZURE_LANGUAGE_ENDPOINT', 'your-endpoint-here')
PROJECT_NAME = os.getenv('AZURE_PROJECT_NAME', 'your-project-name')
DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME', 'your-deployment-name')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not username or not password or not role:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username=? AND role=?', (username, role))
    user = cur.fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return jsonify({'success': True, 'message': f'Welcome, {role} {username}!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/add_book', methods=['POST'])
def add_book():
    # Only admin can add books (simple demo check)
    data = request.json
    role = data.get('role')
    if role != 'admin':
        return jsonify({'success': False, 'message': 'Only admin can add books.'}), 403
    book_name = data.get('book_name')
    author_name = data.get('author_name')
    if not book_name or not author_name:
        return jsonify({'success': False, 'message': 'Missing book name or author name'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO books (book_name, author_name) VALUES (?, ?)', (book_name, author_name))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Book added successfully!'}), 201

@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, book_name, author_name FROM books')
    books = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'books': books}), 200

@app.route('/search_books', methods=['GET'])
def search_books():
    book_name = request.args.get('book_name', '')
    author_name = request.args.get('author_name', '')
    conn = get_db_connection()
    cur = conn.cursor()
    query = 'SELECT id, book_name, author_name FROM books WHERE 1=1'
    params = []
    if book_name:
        query += ' AND book_name LIKE ?'
        params.append(f"%{book_name}%")
    if author_name:
        query += ' AND author_name LIKE ?'
        params.append(f"%{author_name}%")
    cur.execute(query, params)
    books = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'books': books}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'success': False, 'message': 'No message provided'}), 400

        # Initialize the Azure Language Service client
        client = ConversationAnalysisClient(
            LANGUAGE_ENDPOINT,
            AzureKeyCredential(LANGUAGE_KEY)
        )

        # Call the Language Service
        result = client.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "id": "1",
                        "text": user_message,
                        "modality": "text",
                        "language": "en",
                        "participantId": "user1"
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": PROJECT_NAME,
                    "deploymentName": DEPLOYMENT_NAME,
                    "verbose": True
                }
            }
        )

        # Extract the bot's response
        predicted_intent = result["result"]["prediction"]["topIntent"]
        confidence_score = result["result"]["prediction"]["intents"][0]["confidenceScore"]
        
        return jsonify({
            'success': True,
            'intent': predicted_intent,
            'confidence': confidence_score,
            'original_message': user_message
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Create issued_books table if it doesn't exist ---
def create_issued_books_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')
    conn.commit()
    conn.close()

create_issued_books_table()

# --- Get Issued Books for Student ---

# --- Admin: Get All Issued Books ---
@app.route('/all_issued_books', methods=['GET'])
def all_issued_books():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT ib.student_username, b.book_name, b.author_name, ib.issue_date
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.id
        WHERE ib.return_date IS NULL
        ORDER BY ib.issue_date DESC
    ''')
    issued = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'issued': issued}), 200

@app.route('/issued_books', methods=['GET'])
def get_issued_books():
    student_username = request.args.get('student_username')
    if not student_username:
        return jsonify({'success': False, 'message': 'Missing student_username'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT b.id, b.book_name, b.author_name, ib.issue_date
        FROM issued_books ib
        JOIN books b ON ib.book_id = b.id
        WHERE ib.student_username=? AND ib.return_date IS NULL
        ORDER BY ib.issue_date DESC
    ''', (student_username,))
    books = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'books': books}), 200

# --- Issue Book Endpoint ---
@app.route('/issue_book', methods=['POST'])
def issue_book():
    data = request.json
    role = data.get('role')
    student_username = data.get('student_username')
    book_id = data.get('book_id')
    if role != 'student':
        return jsonify({'success': False, 'message': 'Only students can issue books.'}), 403
    if not student_username or not book_id:
        return jsonify({'success': False, 'message': 'Missing student username or book id.'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    # Prevent duplicate issue (same student, same book, not yet returned)
    cur.execute('SELECT * FROM issued_books WHERE student_username=? AND book_id=? AND return_date IS NULL', (student_username, book_id))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Book already issued to this student and not yet returned.'}), 409
    import datetime
    issue_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('INSERT INTO issued_books (student_username, book_id, issue_date) VALUES (?, ?, ?)', (student_username, book_id, issue_date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Book issued successfully!'}), 201

# --- Return Book Endpoint ---
@app.route('/return_book', methods=['POST'])
def return_book():
    import datetime
    data = request.json
    student_username = data.get('student_username')
    book_id = data.get('book_id')
    if not student_username or not book_id:
        return jsonify({'success': False, 'message': 'Missing student username or book id.'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    # Find the issued book record
    cur.execute('SELECT id, issue_date, return_date FROM issued_books WHERE student_username=? AND book_id=? AND return_date IS NULL', (student_username, book_id))
    issued = cur.fetchone()
    if not issued:
        conn.close()
        return jsonify({'success': False, 'message': 'No such issued book found.'}), 404
    issue_date = datetime.datetime.strptime(issued['issue_date'], '%Y-%m-%d %H:%M:%S')
    return_date = datetime.datetime.now()
    days_held = (return_date - issue_date).days
    fine = 0
    if days_held > 7:
        fine = (days_held - 7) * 2
    # Update the return_date
    cur.execute('UPDATE issued_books SET return_date=? WHERE id=?', (return_date.strftime('%Y-%m-%d %H:%M:%S'), issued['id']))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Book returned successfully!', 'fine': fine, 'days_held': days_held}), 200

if __name__ == '__main__':
    app.run(debug=True)
