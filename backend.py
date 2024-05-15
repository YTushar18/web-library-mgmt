from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient('env-var') #Update env variable
db = client['library_db']
users_collection = db['users']
books_collection = db['books']

@app.route('/book/<book_id>', methods=['GET'])
def get_book(book_id):
    book = books_collection.find_one({"_id": book_id})
    if book:
        return jsonify({"id": str(book["_id"]), "title": book["title"], "author": book["author"], "status": book["status"]}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if users_collection.find_one({"username": username}):
        return jsonify({'message': 'User already exists'}), 400
    new_user = {"username": username, "password": password}
    users_collection.insert_one(new_user)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'GET':
        books = books_collection.find()
        books_dict = {str(book["_id"]): {"title": book["title"], "author": book["author"], "status": book["status"]} for book in books}
        response = jsonify(books_dict)
        response.headers['X-Custom-Header'] = 'CustomHeader'
        return response
    elif request.method == 'POST':
        data = request.json
        book_id = data.get('book_id')
        book_info = data.get('book_info')
        if books_collection.find_one({"_id": book_id}):
            return jsonify({'message': 'Book already exists'}), 400
        new_book = {"_id": book_id, "title": book_info['title'], "author": book_info['author'], "status": 'available'}
        books_collection.insert_one(new_book)
        return jsonify({'message': 'Book added successfully'}), 201
    
@app.route('/books/bulk', methods=['POST'])
def add_books_bulk():
    data = request.json
    books = data.get('books', [])
    results = {"added": [], "failed": []}

    for book in books:
        book_id = book['book_id']
        book_info = book['book_info']
        if books_collection.find_one({"_id": book_id}):
            results["failed"].append({"book_id": book_id, "reason": "Book already exists"})
        else:
            new_book = {"_id": book_id, "title": book_info['title'], "author": book_info['author'], "status": 'available'}
            books_collection.insert_one(new_book)
            results["added"].append({"book_id": book_id, "title": book_info['title']})
    return jsonify(results), 201

@app.route('/issue', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    book = books_collection.find_one({"_id": book_id})
    if not book or book['status'] == 'issued':
        return jsonify({'message': 'Book not available'}), 400
    books_collection.update_one({"_id": book_id}, {"$set": {"status": 'issued'}})
    return jsonify({'message': 'Book issued successfully'}), 200

@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    book = books_collection.find_one({"_id": book_id})
    if not book or book['status'] != 'issued':
        return jsonify({'message': 'Invalid return'}), 400
    books_collection.update_one({"_id": book_id}, {"$set": {"status": 'available'}})
    return jsonify({'message': 'Book returned successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)