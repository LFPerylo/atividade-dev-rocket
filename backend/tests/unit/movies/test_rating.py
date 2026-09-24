import pytest

from app.movies.domain.errors import InvalidRating
from app.movies.domain.rating import RatingSummary, Stars, score_to_stars


@pytest.mark.parametrize(("value", "score"), [(1.0, 2.0), (4.5, 9.0), (5.0, 10.0), (2.5, 5.0)])
def test_stars_convert_to_score_doubling_value(value: float, score: float) -> None:
    assert Stars.from_value(value).to_score() == score


@pytest.mark.parametrize("value", [0.0, 0.5, 5.5, 3.3, -1.0])
def test_stars_reject_values_outside_half_steps_between_one_and_five(value: float) -> None:
    with pytest.raises(InvalidRating):
        Stars.from_value(value)


@pytest.mark.parametrize(
    ("score", "stars"), [(9.8, 4.9), (0.0, 0.0), (10.0, 5.0), (7.25, 3.6), (6.5, 3.3), (6.3, 3.2)]
)
def test_score_to_stars_halves_score_with_one_decimal(score: float, stars: float) -> None:
    assert score_to_stars(score) == stars


def test_rating_summary_without_reviews_has_no_average() -> None:
    summary = RatingSummary(count=0, average_score=None)

    assert summary.average_stars is None


def test_rating_summary_exposes_average_in_stars() -> None:
    summary = RatingSummary(count=3, average_score=8.2)

    assert summary.average_stars == 4.1
