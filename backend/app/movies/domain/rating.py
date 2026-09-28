from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.movies.domain.errors import InvalidRating

MIN_STARS = 1.0
MAX_STARS = 5.0
STAR_STEP = 0.5
SCORE_PER_STAR = 2.0


STARS_PRECISION = Decimal("0.1")


def score_to_stars(score: float) -> float:
    stars = Decimal(str(score)) / Decimal(str(SCORE_PER_STAR))
    return float(stars.quantize(STARS_PRECISION, rounding=ROUND_HALF_UP))


def min_score_displayed_as(stars: float) -> float:
    half_step = STARS_PRECISION / 2
    return float((Decimal(str(stars)) - half_step) * Decimal(str(SCORE_PER_STAR)))


@dataclass(frozen=True, slots=True)
class Stars:
    value: float

    @classmethod
    def from_value(cls, value: float) -> "Stars":
        within_range = MIN_STARS <= value <= MAX_STARS
        on_step = (value / STAR_STEP).is_integer()
        if not (within_range and on_step):
            raise InvalidRating(f"Avaliação deve ser de {MIN_STARS} a {MAX_STARS} estrelas")
        return cls(value)

    def to_score(self) -> float:
        return self.value * SCORE_PER_STAR


@dataclass(frozen=True, slots=True)
class RatingSummary:
    count: int
    average_score: float | None

    @property
    def average_stars(self) -> float | None:
        if self.average_score is None:
            return None
        return score_to_stars(self.average_score)
