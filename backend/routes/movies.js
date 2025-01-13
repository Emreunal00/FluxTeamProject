const express = require('express');
const router = express.Router();
const axios = require('axios');

// Fetch movie data from OMDb API
router.get('/:movieTitle', async (req, res) => {
    const movieTitle = req.params.movieTitle;
    const apiKey = process.env.OMDB_API_KEY;
    
    try {
        const response = await axios.get(`http://www.omdbapi.com/?t=${movieTitle}&apikey=${f91c77a2}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching movie data' });
    }
});

module.exports = router;


fetch('/add_to_favorites', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ movie_data: movieTitle })
})
.then(response => response.json())
.then(data => {
    alert(data.message);
})
.catch(error => console.error('Hata:', error));
