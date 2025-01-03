async function searchMovies() {
    const searchQuery = document.getElementById('search-input').value.trim();
    if (searchQuery) {
        // Fetch data from the backend
        try {
            const response = await fetch(`http://localhost:3001/api/movies/${searchQuery}`);
            const data = await response.json();

            if (data.Response === 'True') {
                displayMoviesList(data.Search);  // Display movie results
            } else {
                alert('No movies found!');
                clearMoviesList();
            }
        } catch (error) {
            alert('Error fetching movie data');
            console.error(error);
        }
    } else {
        alert('Please enter a search query.');
    }
}

function displayMoviesList(movies) {
    const moviesList = document.getElementById('movies-list');
    moviesList.innerHTML = ''; // Clear previous results

    movies.forEach(movie => {
        const movieCard = document.createElement('div');
        movieCard.classList.add('movie-card');
        movieCard.innerHTML = `
            <img src="${movie.Poster}" alt="${movie.Title} Poster" />
            <h3>${movie.Title}</h3>
        `;
        movieCard.onclick = () => displayMovieDetail(movie);
        moviesList.appendChild(movieCard);
    });
}

function clearMoviesList() {
    const moviesList = document.getElementById('movies-list');
    moviesList.innerHTML = ''; // Clear all movie posters
}
