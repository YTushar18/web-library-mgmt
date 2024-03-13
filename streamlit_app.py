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

    # Initialize session state for login status and username
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''

    menu = ["Home", "Login", "Register"]
    if st.session_state['logged_in']:
        menu.extend(["Add Book", "Issue Book", "Return Book", "View All Books", "Logout"])

    choice = st.sidebar.selectbox("Menu", menu)

    if st.session_state['logged_in']:
        st.write(f"Welcome, {st.session_state['username']}!")

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
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()  # Rerun the app to refresh the page
            else:
                st.error(result['message'])

    elif choice == "Add Book" and st.session_state['logged_in']:
        st.subheader("Add Book")
        book_id = st.text_input("Book ID")
        book_title = st.text_input("Book Title")
        book_author = st.text_input("Book Author")
        book_info = {"title": book_title, "author": book_author, "status": "available"}
        if st.button("Add Book"):
            result = add_book(book_id, book_info)
            st.success(result['message'])

    elif choice == "Issue Book" and st.session_state['logged_in']:
        st.subheader("Issue Book")
        book_id = st.text_input("Book ID")
        if st.button("Issue Book"):
            result = issue_book(book_id)
            st.success(result['message'])

    elif choice == "Return Book" and st.session_state['logged_in']:
        st.subheader("Return Book")
        book_id = st.text_input("Book ID")
        if st.button("Return Book"):
            result = return_book(book_id)
            st.success(result['message'])

    elif choice == "View All Books" and st.session_state['logged_in']:
        st.subheader("Available Books")
        books = get_books()
        for book_id, book_info in books.items():
            st.write(f"ID: {book_id}, Title: {book_info['title']}, Author: {book_info['author']}, Status: {book_info['status']}")

    elif choice == "Logout" and st.session_state['logged_in']:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.experimental_rerun()  # Rerun the app to refresh the page
        st.success("You have been logged out.")

    else:
        st.subheader("Home")
        if st.session_state['logged_in']:
            st.write("You are logged in to the Library Management System")
        else:
            st.write("Please log in to access the Library Management System")

if __name__ == '__main__':
    main()
