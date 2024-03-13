import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:5000"  # Adjust if your Flask app is running on a different address

def register_user(username, password):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    return response.json()

def login_user(username, password):
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return response.json()

def add_book(book_id, book_info):
    response = requests.post(f"{BASE_URL}/books", json={"book_id": book_id, "book_info": book_info})
    return response.json()

def get_books():
    response = requests.get(f"{BASE_URL}/books")
    return response.json()

def issue_book(book_id):
    response = requests.post(f"{BASE_URL}/issue", json={"book_id": book_id})
    return response.json()

def return_book(book_id):
    response = requests.post(f"{BASE_URL}/return", json={"book_id": book_id})
    return response.json()

def main():
    st.title("Library Management System")

    menu = ["Home", "Login", "Register", "Add Book", "Issue Book", "Return Book", "View Books"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Register"):
            result = register_user(username, password)
            st.success(result['message'])

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            result = login_user(username, password)
            if result.get('message') == 'Login successful':
                st.success(result['message'])
            else:
                st.error(result['message'])

    elif choice == "Add Book":
        st.subheader("Add Book")
        book_id = st.text_input("Book ID")
        book_title = st.text_input("Book Title")
        book_author = st.text_input("Book Author")
        book_info = {"title": book_title, "author": book_author, "status": "available"}
        if st.button("Add Book"):
            result = add_book(book_id, book_info)
            st.success(result['message'])

    elif choice == "Issue Book":
        st.subheader("Issue Book")
        book_id = st.text_input("Book ID")
        if st.button("Issue Book"):
            result = issue_book(book_id)
            st.success(result['message'])

    elif choice == "Return Book":
        st.subheader("Return Book")
        book_id = st.text_input("Book ID")
        if st.button("Return Book"):
            result = return_book(book_id)
            st.success(result['message'])

    elif choice == "View Books":
        st.subheader("Available Books")
        books = get_books()
        if books:
            for book_id, book_info in books.items():
                st.write(f"ID: {book_id}, Title: {book_info['title']}, Author: {book_info['author']}, Status: {book_info['status']}")
        else:
            st.write("No books available")

    else:
        st.subheader("Home")
        st.write("Welcome to the Library Management System")

if __name__ == '__main__':
    main()
