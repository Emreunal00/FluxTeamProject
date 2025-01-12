class Review:
    def __init__(self, user, movie, content, rating):
        self.user = user
        self.movie = movie
        self.content = content
        self.rating = rating

    def to_dict(self):
        return {
            "user": self.user.to_dict(),
            "movie": self.movie.to_dict(),
            "content": self.content,
            "rating": self.rating
        }