const express = require('express');
const app = express();
const cors = require('cors');
const bodyParser = require('body-parser');
const fetch = require('node-fetch'); // fetch'i import et
require('dotenv').config();

app.use(cors());
app.use(bodyParser.json());

const apiKey = process.env.OMDB_API_KEY || 'f91c77a2';

// Film arama rotası
app.get('/api/movies/:query', async (req, res) => {
    const query = req.params.query;
    try {
        const response = await fetch(`http://www.omdbapi.com/?s=${query}&apikey=${apiKey}`);
        const data = await response.json();

        if (data.Response === 'True') {
            res.json(data);
        } else {
            res.status(404).json({ error: data.Error || 'No movies found' });
        }
    } catch (error) {
        console.error('Error fetching movie data:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

// Ana rota
app.get('/', (req, res) => {
    res.send('Welcome to the Movie Database API');
});

const port = 3001;
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
