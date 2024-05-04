from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import sqlite3
import jwt
from passlib.context import CryptContext
from contextlib import contextmanager

# Database connection
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('library.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize FastAPI app
app = FastAPI()

# Database setup function
def setup_database():
    with get_db_connection() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS User (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS Books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                status TEXT NOT NULL
            );
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS IssueBooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (book_id) REFERENCES Books (id),
                FOREIGN KEY (user_id) REFERENCES Users (id)
            );
        ''')
        db.commit()

# Call the setup_database function when the application starts
setup_database()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Book(BaseModel):
    id: int
    name: str
    title: str
    author: str
    status: str

class User(BaseModel):
    username: str
    password: str
    email: str

class IssueBook(BaseModel):
    book_id: int
    user_id: int

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    with get_db_connection() as db:
        user = db.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user

def create_access_token(data: dict):
    return jwt.encode(data, "SECRET_KEY")

# Endpoints
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register_user(user: User):
    with get_db_connection() as db:
        hashed_password = get_password_hash(user.password)
        db.execute('INSERT INTO User (username, password, email) VALUES (?, ?, ?)', (user.username, hashed_password, user.email))
        db.commit()
    return {"message": "User registered successfully"}

@app.get("/books", response_model=List[Book])
async def get_books():
    with get_db_connection() as db:
        books = db.execute('SELECT * FROM Books').fetchall()
    return books

@app.post("/books")
async def add_book(book: Book):
    with get_db_connection() as db:
        db.execute('INSERT INTO Books (name, title, author, status) VALUES (?, ?, ?, ?)', (book.name, book.title, book.author, book.status))
        db.commit()
    return {"message": "Book added successfully"}

@app.delete("/books/{book_id}")
async def remove_book(book_id: int):
    with get_db_connection() as db:
        db.execute('DELETE FROM Books WHERE id = ?', (book_id,))
        db.commit()
    return {"message": "Book removed successfully"}

@app.post("/issue")
async def issue_book(issue: IssueBook):
    with get_db_connection() as db:
        db.execute('INSERT INTO IssueBooks (book_id, user_id) VALUES (?, ?)', (issue.book_id, issue.user_id))
        db.execute('UPDATE Books SET status = "issued" WHERE id = ?', (issue.book_id,))
        db.commit()
    return {"message": "Book issued successfully"}

@app.post("/return")
async def return_book(issue: IssueBook):
    with get_db_connection() as db:
        db.execute('DELETE FROM IssueBooks WHERE book_id = ? AND user_id = ?', (issue.book_id, issue.user_id))
        db.execute('UPDATE Books SET status = "available" WHERE id = ?', (issue.book_id,))
        db.commit()
    return {"message": "Book returned successfully"}

@app.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    return {"message": "User logged out"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
