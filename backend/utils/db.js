const fs = require('fs');

function readData(file) {
    return new Promise((resolve, reject) => {
        fs.readFile(file, (err, data) => {
            if (err) reject(err);
            resolve(JSON.parse(data));
        });
    });
}

function writeData(file, data) {
    return new Promise((resolve, reject) => {
        fs.writeFile(file, JSON.stringify(data, null, 2), (err) => {
            if (err) reject(err);
            resolve();
        });
    });
}

module.exports = { readData, writeData };