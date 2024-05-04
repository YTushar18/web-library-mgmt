
import streamlit as st
import requests

BASE_URL = "http://localhost:8000"  # Change this to your FastAPI server URL

# Helper functions for API calls
def register_user(username, password, email):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password, "email": email})
    return response.json()

def login(username, password):
    response = requests.post(f"{BASE_URL}/token", data={"username": username, "password": password})
    return response.json()

def get_books(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/books", headers=headers)
    return response.json()

def add_book(token, name, title, author, status):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/books", headers=headers, json={"name": name, "title": title, "author": author, "status": status})
    return response.json()

def remove_book(token, book_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)
    return response.json()

# Streamlit UI
st.title("Library Management System")

menu = ["Home", "Login", "Register", "View Books", "Add Book", "Remove Book"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to the Library Management System")

elif choice == "Register":
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    if st.button("Register"):
        response = register_user(username, password, email)
        st.success(response["message"])

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = login(username, password)
        if "access_token" in response:
            st.success("Logged in successfully")
            st.session_state["token"] = response["access_token"]
        else:
            st.error("Login failed")

elif choice == "View Books":
    st.subheader("View Books")
    if "token" in st.session_state:
        books = get_books(st.session_state["token"])
        for book in books:
            st.write(book)
    else:
        st.warning("Please login to view books")

elif choice == "Add Book":
    st.subheader("Add Book")
    if "token" in st.session_state:
        name = st.text_input("Name")
        title = st.text_input("Title")
        author = st.text_input("Author")
        status = st.selectbox("Status", ["available", "issued"])
        if st.button("Add Book"):
            response = add_book(st.session_state["token"], name, title, author, status)
            st.success(response["message"])
    else:
        st.warning("Please login to add a book")

elif choice == "Remove Book":
    st.subheader("Remove Book")
    if "token" in st.session_state:
        book_id = st.number_input("Book ID", min_value=1, step=1, format="%d")
        if st.button("Remove Book"):
            response = remove_book(st.session_state["token"], book_id)
            st.success(response["message"])
    else:
        st.warning("Please login to remove a book")

