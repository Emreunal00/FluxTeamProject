import streamlit as st
from pages.search_movies import search_movies
from pages.user_reviews import user_reviews

def main():
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to:", ["Search Movies", "User Reviews"])

    if choice == "Search Movies":
        search_movies()
    elif choice == "User Reviews":
        user_reviews()

if __name__ == "__main__":
    main()
