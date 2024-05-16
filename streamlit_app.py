import streamlit as st
import requests
import pandas as pd
import io

BASE_URL = "http://127.0.0.1:5000"

def register_user(username, password):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    return response.json()

def login_user(username, password):
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return response.json()

def add_book(token, book_id, book_info):
    headers = {'x-access-token': token}
    response = requests.post(f"{BASE_URL}/books", json={"book_id": book_id, "book_info": book_info}, headers=headers)
    return response.json()

def add_books_bulk(token, books):
    headers = {'x-access-token': token}
    response = requests.post(f"{BASE_URL}/books/bulk", json={"books": books}, headers=headers)
    return response.json()

def get_books(token):
    headers = {'x-access-token': token}
    response = requests.get(f"{BASE_URL}/books", headers=headers)
    return response.json()

def get_book_details(token, book_id):
    headers = {'x-access-token': token}
    response = requests.get(f"{BASE_URL}/book/{book_id}", headers=headers)
    if response.status_code == 200:
        return response.json(), True
    else:
        return response.json(), False

def issue_book(token, book_id):
    headers = {'x-access-token': token}
    response = requests.post(f"{BASE_URL}/issue", json={"book_id": book_id}, headers=headers)
    return response.json()

def return_book(token, book_id):
    headers = {'x-access-token': token}
    response = requests.post(f"{BASE_URL}/return", json={"book_id": book_id}, headers=headers)
    return response.json()

def main():
    st.title("Library Management System")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['token'] = ''

    menu = ["Home", "Login", "Register", "View Book Details"]
    if st.session_state['logged_in']:
        menu = ["Home", "Add Book", "Issue Book", "Return Book", "View All Books", "Logout"]

    choice = st.sidebar.selectbox("Menu", menu)

    if st.session_state['logged_in']:
        st.write(f"Welcome, {st.session_state['username']}!")

    if choice == "Register":
        username, password = st.text_input("Username"), st.text_input("Password", type='password')
        if st.button("Register"):
            result = register_user(username, password)
            st.success(result['message'])

    elif choice == "Login":
        username, password = st.text_input("Username"), st.text_input("Password", type='password')
        if st.button("Login"):
            result = login_user(username, password)
            if 'token' in result:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['token'] = result['token']
                st.experimental_rerun()
            else:
                st.error(result['message'])

    elif choice == "View Book Details":
        book_id = st.text_input("Enter the Book ID to view details")
        if st.button("Get Details"):
            book_details, success = get_book_details(st.session_state['token'], book_id)
            if success:
                st.write(f"ID: {book_details['id']}, Title: {book_details['title']}, Author: {book_details['author']}, Status: {book_details['status']}")
            else:
                st.error("Book not found. Please check the Book ID and try again.")

    elif choice == "Add Book" and st.session_state['logged_in']:
        st.subheader("Add Book")
        book_id = st.text_input("Book ID")
        book_title = st.text_input("Book Title")
        book_author = st.text_input("Book Author")
        book_info = {"title": book_title, "author": book_author, "status": "available"}
        if st.button("Add Book"):
            result = add_book(st.session_state['token'], book_id, book_info)
            st.success(result['message'])

        st.subheader("Upload Book List")
        uploaded_file = st.file_uploader("Choose a CSV or TXT file", type=["csv", "txt"])
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode("utf-8").strip().splitlines()
                st.write("File content preview:", content[:5])  # Show the first 5 lines of the file for debugging

                # Read header and validate
                header = content[0].split(',')
                required_columns = {"Book ID", "Book Title", "Book Author"}
                if not required_columns.issubset(set(map(str.strip, header))):
                    st.error(f"File must contain columns: {', '.join(required_columns)}")
                else:
                    books = []
                    for line in content[1:]:  # Skip header
                        book_data = line.split(',')
                        if len(book_data) != 3:
                            st.error(f"Invalid format in line: {line}")
                            continue
                        book_id = book_data[0].strip()
                        book_title = book_data[1].strip()
                        book_author = book_data[2].strip()
                        book_info = {"title": book_title, "author": book_author, "status": "available"}
                        books.append({"book_id": book_id, "book_info": book_info})

                    if st.button("Upload Book List"):
                        result = add_books_bulk(st.session_state['token'], books)
                        st.write("Books successfully added:")
                        for book in result['added']:
                            st.write(f"ID: {book['book_id']}, Title: {book['title']}")
                        st.write("Books failed to add:")
                        for book in result['failed']:
                            st.write(f"ID: {book['book_id']}, Reason: {book['reason']}")
            except Exception as e:
                st.error(f"Error processing file: {e}")

    elif choice == "Issue Book" and st.session_state['logged_in']:
        st.subheader("Issue Book")
        book_id = st.text_input("Book ID")
        if st.button("Issue Book"):
            result = issue_book(st.session_state['token'], book_id)
            st.success(result['message'])

    elif choice == "Return Book" and st.session_state['logged_in']:
        st.subheader("Return Book")
        book_id = st.text_input("Book ID")
        if st.button("Return Book"):
            result = return_book(st.session_state['token'], book_id)
            st.success(result['message'])

    elif choice == "View All Books" and st.session_state['logged_in']:
        st.subheader("Available Books")
        books = get_books(st.session_state['token'])
        for book_id, book_info in books.items():
            st.write(f"ID: {book_id}, Title: {book_info['title']}, Author: {book_info['author']}, Status: {book_info['status']}")

    elif choice == "Logout" and st.session_state['logged_in']:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.session_state['token'] = ''
        st.experimental_rerun()
        st.success("You have been logged out.")

    else:
        st.subheader("Home")
        if st.session_state['logged_in']:
            st.write("You are logged in to the Library Management System")
        else:
            st.write("Please log in to access the Library Management System")

if __name__ == '__main__':
    main()
