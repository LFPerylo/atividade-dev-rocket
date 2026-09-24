class DomainError(Exception):
    pass


class InvalidRating(DomainError):
    pass


class InvalidQuery(DomainError):
    pass


class InvalidMovieData(DomainError):
    pass


class InvalidReview(DomainError):
    pass


class MovieNotFound(DomainError):
    def __init__(self, movie_id: str) -> None:
        super().__init__(f"Filme {movie_id} não encontrado")
        self.movie_id = movie_id


class GenreNotFound(DomainError):
    def __init__(self, genre_ids: set[str]) -> None:
        super().__init__(f"Gêneros inexistentes: {', '.join(sorted(genre_ids))}")
        self.genre_ids = genre_ids
