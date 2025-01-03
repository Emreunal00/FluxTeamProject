const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');  // Import CORS
const app = express();
const port = 3000;

app.use(cors());  // Enable CORS for all routes

app.get('/api/movies/:query', async (req, res) => {
    const query = req.params.query;
    const apiKey = 'f91c77a2';  // Replace with your actual OMDb API key

    try {
        const response = await fetch(`http://www.omdbapi.com/?s=${query}&apikey=${f91c77a2}`);
        const data = await response.json();

        if (data.Response === 'True') {
            res.json(data);  // Return movie search results
        } else {
            res.json({ Response: 'False', Message: 'No movies found' });
        }
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch movie data' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
