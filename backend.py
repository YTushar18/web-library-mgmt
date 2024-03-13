from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory "database" for simplicity
users = {}
books = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return jsonify({'message': 'User already exists'}), 400
    users[username] = {'password': password}
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username not in users or users[username]['password'] != password:
        return jsonify({'message': 'Invalid credentials'}), 401
    return jsonify({'message': 'Login successful'}), 200

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'GET':
        return jsonify(books)
    elif request.method == 'POST':
        data = request.json
        book_id = data.get('book_id')
        book_info = data.get('book_info')
        books[book_id] = book_info
        return jsonify({'message': 'Book added successfully'}), 201

@app.route('/issue', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    if book_id not in books or books[book_id].get('status') == 'issued':
        return jsonify({'message': 'Book not available'}), 400
    books[book_id]['status'] = 'issued'
    return jsonify({'message': 'Book issued successfully'}), 200

@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    if book_id not in books or books[book_id].get('status') != 'issued':
        return jsonify({'message': 'Invalid return'}), 400
    books[book_id]['status'] = 'available'
    return jsonify({'message': 'Book returned successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
