from datetime import date, datetime
from typing import Any

import pytest

from app.movies.domain.entities import MovieDraft, NewReview, Review
from app.movies.domain.errors import InvalidMovieData, InvalidReview
from app.movies.domain.rating import Stars


def make_draft(**overrides: Any) -> MovieDraft:
    values: dict[str, Any] = {
        "title": "Cidade de Deus",
        "directors": ("Fernando Meirelles",),
        "genre_ids": ("g-drama",),
        "release_year": 2002,
    }
    values.update(overrides)
    return MovieDraft(**values)


def test_draft_trims_title_and_director_names() -> None:
    draft = make_draft(title="  Cidade de Deus ", directors=(" Fernando Meirelles ", " "))

    assert draft.title == "Cidade de Deus"
    assert draft.directors == ("Fernando Meirelles",)


def test_draft_requires_title() -> None:
    with pytest.raises(InvalidMovieData):
        make_draft(title="   ")


def test_draft_derives_year_from_release_date() -> None:
    draft = make_draft(release_year=None, release_date=date(2002, 8, 30))

    assert draft.release_year == 2002


def test_draft_rejects_year_different_from_release_date() -> None:
    with pytest.raises(InvalidMovieData):
        make_draft(release_year=2001, release_date=date(2002, 8, 30))


@pytest.mark.parametrize("year", [1800, 2200])
def test_draft_rejects_implausible_year(year: int) -> None:
    with pytest.raises(InvalidMovieData):
        make_draft(release_year=year)


def test_draft_rejects_negative_runtime() -> None:
    with pytest.raises(InvalidMovieData):
        make_draft(runtime_minutes=-5)


def test_draft_removes_duplicated_genres_preserving_order() -> None:
    draft = make_draft(genre_ids=("g-drama", "g-crime", "g-drama"))

    assert draft.genre_ids == ("g-drama", "g-crime")


def test_new_review_requires_author_and_comment() -> None:
    with pytest.raises(InvalidReview):
        NewReview(author=" ", stars=Stars.from_value(4), comment="Ótimo")
    with pytest.raises(InvalidReview):
        NewReview(author="Ana", stars=Stars.from_value(4), comment="  ")


def test_new_review_trims_text() -> None:
    review = NewReview(author=" Ana ", stars=Stars.from_value(4), comment=" Ótimo filme ")

    assert (review.author, review.comment) == ("Ana", "Ótimo filme")


def test_review_exposes_stars_from_score() -> None:
    review = Review(
        id="r1",
        movie_id="m1",
        author="Ana",
        score=9.0,
        comment="Excelente",
        created_at=datetime(2026, 9, 24),
    )

    assert review.stars == 4.5
