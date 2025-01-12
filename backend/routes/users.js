const express = require('express');
const router = express.Router();
const fs = require('fs');
const bcrypt = require('bcrypt');

// Register a new user
router.post('/register', (req, res) => {
    const { username, password } = req.body;
    
    // Check if user already exists
    fs.readFile('./backend/utils/users.json', (err, data) => {
        if (err) return res.status(500).json({ error: 'Internal server error' });

        const users = JSON.parse(data);
        const userExists = users.find(user => user.username === username);
        if (userExists) return res.status(400).json({ error: 'User already exists' });

        // Hash the password
        bcrypt.hash(password, 10, (err, hashedPassword) => {
            if (err) return res.status(500).json({ error: 'Error hashing password' });

            // Save user
            const newUser = { username, password: hashedPassword };
            users.push(newUser);
            fs.writeFile('./backend/utils/users.json', JSON.stringify(users, null, 2), (err) => {
                if (err) return res.status(500).json({ error: 'Error saving user' });
                res.status(200).json({ message: 'User registered successfully' });
            });
        });
    });
});

// Login a user
router.post('/login', (req, res) => {
    const { username, password } = req.body;

    fs.readFile('./backend/utils/users.json', (err, data) => {
        if (err) return res.status(500).json({ error: 'Internal server error' });

        const users = JSON.parse(data);
        const user = users.find(u => u.username === username);
        if (!user) return res.status(404).json({ error: 'User not found' });

        // Compare password
        bcrypt.compare(password, user.password, (err, isMatch) => {
            if (err) return res.status(500).json({ error: 'Error comparing passwords' });
            if (!isMatch) return res.status(401).json({ error: 'Invalid password' });
            res.status(200).json({ message: 'Login successful' });
        });
    });
});

module.exports = router;