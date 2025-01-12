class Movie:
    def __init__(self, title, genre, release_year):
        self.title = title
        self.genre = genre
        self.release_year = release_year

    def to_dict(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "release_year": self.release_year
        }
