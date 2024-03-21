from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Book(db.Model):
    id = db.Column(db.String(50), primary_key=True) 
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    status = db.Column(db.String(20), default='available')

@app.route('/book/<book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book:
        return jsonify({"id": book.id, "title": book.title, "author": book.author, "status": book.status}), 200
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/register', methods=['POST'])
def register():
    if request.content_type == 'application/json':
        data = request.json
    else:
        data = request.form
    username = data.get('username')
    password = data.get('password')
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     user = User.query.filter_by(username=username, password=password).first()
#     if user:
#         # Redirect to the view_books endpoint after successful login
#         return redirect(url_for('view_books'))
#     else:
#         return jsonify({'message': 'Invalid credentials'}), 401

# @app.route('/view_books', methods=['GET'])
# def view_books():
#     books_query = Book.query.all()
#     books = {book.id: {"title": book.title, "author": book.author, "status": book.status} for book in books_query}
#     return jsonify(books)    

@app.route('/books', methods=['GET', 'POST'])
def manage_books():
    if request.method == 'GET':
        books_query = Book.query.all()
        books = {book.id: {"title": book.title, "author": book.author, "status": book.status} for book in books_query}
        response = jsonify(books)
        response.headers['X-Custom-Header'] = 'CustomHeader'
        return response
    elif request.method == 'POST':
        data = request.json
        book_id = data.get('book_id')
        book_info = data.get('book_info')
        if Book.query.filter_by(id=book_id).first():
            return jsonify({'message': 'Book already exists'}), 400
        new_book = Book(id=book_id, title=book_info['title'], author=book_info['author'], status='available')
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201

@app.route('/issue', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    book = Book.query.filter_by(id=book_id).first()
    if not book or book.status == 'issued':
        return jsonify({'message': 'Book not available'}), 400
    book.status = 'issued'
    db.session.commit()
    return jsonify({'message': 'Book issued successfully'}), 200

@app.route('/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    book = Book.query.filter_by(id=book_id).first()
    if not book or book.status != 'issued':
        return jsonify({'message': 'Invalid return'}), 400
    book.status = 'available'
    db.session.commit()
    return jsonify({'message': 'Book returned successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)