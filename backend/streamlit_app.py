import streamlit as st
import requests

# Title
st.title('Movie Database')
st.write('Welcome to the Movie Database!')

# Fetch movies from the Flask API
with st.spinner("Fetching movies from the API..."):
    try:
        response = requests.get("http://127.0.0.1:5000/api/movies", timeout=5)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.ConnectionError:
        st.error("Connection error: Unable to reach the API. Is the Flask server running?")
    except requests.exceptions.Timeout:
        st.error("Timeout error: The API took too long to respond.")
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    else:
        # Check the response status code
        st.write(f"Response Status Code: {response.status_code}")

        try:
            # Parse the JSON response
            movies = response.json()
            if movies:
                st.write("Movies List:")
                # Display movies in a readable format
                for movie in movies:
                    st.write(f"**Title:** {movie.get('title', 'No Title')}")
                    st.write(f"**Description:** {movie.get('description', 'No Description')}")
                    st.write("---")
            else:
                st.write("No movies found.")
        except ValueError:
            st.error("Failed to parse JSON data from the API response.")

# Debugging Option: Show raw API response
if st.checkbox("Show raw API response"):
    st.json(response.text if 'response' in locals() and response.ok else {})