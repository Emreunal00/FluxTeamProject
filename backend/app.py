import streamlit as st
import requests

# Başlık
st.title('Movie Database')
st.write('Welcome to the Movie Database!')

# API'den veri çekme
response = requests.get("http://127.0.0.1:5000/api/movies")  # Flask API'nin yeni portunu kullan

# Yanıtın durumunu kontrol et
st.write(f"Response Status Code: {response.status_code}")

if response.status_code == 200:
    try:
        # Gelen JSON verisini çözümle
        movies = response.json()
        if movies:
            st.write("Movies List:")
            # Filmleri daha okunabilir şekilde listelemek için
            for movie in movies:
                st.write(f"**Title:** {movie.get('title', 'No Title')}")
                st.write(f"**Description:** {movie.get('description', 'No Description')}")
                st.write("---")
        else:
            st.write("No movies found.")
    except ValueError:
        st.error("JSON verisi alınamadı!")
else:
    st.error(f"API isteği başarısız oldu! Status code: {response.status_code}")
