from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "saduhb2378gfd08473gfy83dbwshb2370bd0u27behwbd0837b80b"
bcrypt = Bcrypt(app)
CORS(app)

client = MongoClient('mongodb+srv://iabhishekapp:BNYopb29Qevxi8Ch@backendpro.5qozij5.mongodb.net/?retryWrites=true&w=majority&appName=BackendPro',
                     tlsCAFile=certifi.where()) #Update env variable

db = client['library_db']
users_collection = db['users']
books_collection = db['books']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is invalid! Signature has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': f'Token is invalid! {str(e)}'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Check if user already exists
    if users_collection.find_one({'username': username}):
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = {
        "username": username,
        "password": hashed_password
    }
    result = users_collection.insert_one(new_user)
    new_user['_id'] = str(result.inserted_id)
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = users_collection.find_one({'username': username})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid username or password!'}), 401
    
    expiration = datetime.utcnow() + timedelta(minutes=30)
    
    token = jwt.encode({'user_id': str(user['_id']), 'exp': expiration}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token})

@app.route('/books', methods=['GET', 'POST'])
@token_required
def manage_books(current_user):
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
@token_required
def add_books_bulk(current_user):
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
@token_required
def issue_book(current_user):
    data = request.json
    book_id = data.get('book_id')
    book = books_collection.find_one({"_id": book_id})
    if not book or book['status'] == 'issued':
        return jsonify({'message': 'Book not available'}), 400
    books_collection.update_one({"_id": book_id}, {"$set": {"status": 'issued'}})
    return jsonify({'message': 'Book issued successfully'}), 200

@app.route('/return', methods=['POST'])
@token_required
def return_book(current_user):
    data = request.json
    book_id = data.get('book_id')
    book = books_collection.find_one({"_id": book_id})
    if not book or book['status'] != 'issued':
        return jsonify({'message': 'Invalid return'}), 400
    books_collection.update_one({"_id": book_id}, {"$set": {"status": 'available'}})
    return jsonify({'message': 'Book returned successfully'}), 200


@app.route('/book/<book_id>', methods=['GET'])
@token_required
def get_book(current_user, book_id):
    book = books_collection.find_one({"_id": book_id})
    if book:
        return jsonify({"id": str(book["_id"]), "title": book["title"], "author": book["author"], "status": book["status"]}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)