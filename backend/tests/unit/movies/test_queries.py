import pytest

from app.movies.domain.errors import InvalidQuery
from app.movies.domain.queries import MovieFilters, Page, PageRequest, SortField, SortOrder


def test_page_request_computes_offset() -> None:
    assert PageRequest(page=3, size=20).offset == 40


@pytest.mark.parametrize(("page", "size"), [(0, 20), (1, 0), (1, 101)])
def test_page_request_rejects_invalid_bounds(page: int, size: int) -> None:
    with pytest.raises(InvalidQuery):
        PageRequest(page=page, size=size)


@pytest.mark.parametrize(("total", "pages"), [(0, 0), (1, 1), (20, 1), (21, 2)])
def test_page_counts_pages_from_total(total: int, pages: int) -> None:
    page: Page[str] = Page(items=[], total=total, request=PageRequest(page=1, size=20))

    assert page.pages == pages


def test_movie_filters_reject_inverted_year_range() -> None:
    with pytest.raises(InvalidQuery):
        MovieFilters(year_from=2020, year_to=2010)


def test_movie_filters_strip_blank_search_term() -> None:
    assert MovieFilters(search="   ").search is None
    assert MovieFilters(search="  Matrix ").search == "Matrix"


def test_movie_filters_reject_min_stars_outside_scale() -> None:
    with pytest.raises(InvalidQuery):
        MovieFilters(min_stars=6)


def test_movie_filters_default_to_most_popular_first() -> None:
    filters = MovieFilters()

    assert (filters.sort, filters.order) == (SortField.POPULARITY, SortOrder.DESC)
