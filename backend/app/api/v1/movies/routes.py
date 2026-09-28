from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status

from app.api.v1.dependencies import (
    CurrentAdmin,
    GenreRepositoryDep,
    MovieRepositoryDep,
    ReviewRepositoryDep,
    TransactionDep,
)
from app.api.v1.movies.schemas import (
    MovieDetailsOut,
    MovieIn,
    MovieSummaryOut,
    ReviewIn,
    ReviewOut,
)
from app.api.v1.schemas import PageOut
from app.movies.application.movie_use_cases import (
    CreateMovie,
    DeleteMovie,
    GetMovieDetails,
    ListMovies,
    UpdateMovie,
)
from app.movies.application.review_use_cases import AddReview, ListReviews
from app.movies.domain.queries import (
    MAX_PAGE_SIZE,
    MovieFilters,
    PageRequest,
    SortField,
    SortOrder,
)

router = APIRouter(prefix="/movies", tags=["movies"])

PageNumber = Annotated[int, Query(alias="pagina", ge=1)]
PageSize = Annotated[int, Query(alias="tamanho", ge=1, le=MAX_PAGE_SIZE)]


@router.get("")
async def list_movies(
    movies: MovieRepositoryDep,
    page: PageNumber = 1,
    size: PageSize = 20,
    search: Annotated[str | None, Query(alias="busca", max_length=200)] = None,
    genre_id: Annotated[str | None, Query(alias="genero")] = None,
    year_from: Annotated[int | None, Query(alias="ano_de")] = None,
    year_to: Annotated[int | None, Query(alias="ano_ate")] = None,
    min_stars: Annotated[float | None, Query(alias="estrelas_min")] = None,
    sort: Annotated[SortField, Query(alias="ordenar")] = SortField.POPULARITY,
    order: Annotated[SortOrder, Query(alias="ordem")] = SortOrder.DESC,
) -> PageOut[MovieSummaryOut]:
    filters = MovieFilters(
        search=search,
        genre_id=genre_id,
        year_from=year_from,
        year_to=year_to,
        min_stars=min_stars,
        sort=sort,
        order=order,
    )
    result = await ListMovies(movies).execute(filters, PageRequest(page=page, size=size))
    return PageOut[MovieSummaryOut].build(result, MovieSummaryOut.from_summary)


@router.get("/{movie_id}")
async def get_movie(movie_id: str, movies: MovieRepositoryDep) -> MovieDetailsOut:
    return MovieDetailsOut.from_details(await GetMovieDetails(movies).execute(movie_id))


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_movie(
    payload: MovieIn,
    request: Request,
    response: Response,
    _: CurrentAdmin,
    movies: MovieRepositoryDep,
    genres: GenreRepositoryDep,
    transaction: TransactionDep,
) -> MovieDetailsOut:
    movie = await CreateMovie(movies, genres, transaction).execute(payload.to_draft())
    response.headers["Location"] = str(request.url_for("get_movie", movie_id=movie.id))
    return MovieDetailsOut.from_details(movie)


@router.put("/{movie_id}")
async def update_movie(
    movie_id: str,
    payload: MovieIn,
    _: CurrentAdmin,
    movies: MovieRepositoryDep,
    genres: GenreRepositoryDep,
    transaction: TransactionDep,
) -> MovieDetailsOut:
    movie = await UpdateMovie(movies, genres, transaction).execute(movie_id, payload.to_draft())
    return MovieDetailsOut.from_details(movie)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: str, _: CurrentAdmin, movies: MovieRepositoryDep, transaction: TransactionDep
) -> None:
    await DeleteMovie(movies, transaction).execute(movie_id)


@router.get("/{movie_id}/reviews")
async def list_reviews(
    movie_id: str,
    movies: MovieRepositoryDep,
    reviews: ReviewRepositoryDep,
    page: PageNumber = 1,
    size: PageSize = 10,
) -> PageOut[ReviewOut]:
    result = await ListReviews(movies, reviews).execute(movie_id, PageRequest(page, size))
    return PageOut[ReviewOut].build(result, ReviewOut.from_review)


@router.post("/{movie_id}/reviews", status_code=status.HTTP_201_CREATED)
async def add_review(
    movie_id: str,
    payload: ReviewIn,
    _: CurrentAdmin,
    movies: MovieRepositoryDep,
    reviews: ReviewRepositoryDep,
    transaction: TransactionDep,
) -> ReviewOut:
    review = await AddReview(movies, reviews, transaction).execute(
        movie_id, payload.to_new_review()
    )
    return ReviewOut.from_review(review)
