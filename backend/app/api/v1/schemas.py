from collections.abc import Callable, Sequence

from pydantic import BaseModel, ConfigDict

from app.movies.domain.queries import Page


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageOut[T](ApiModel):
    itens: list[T]
    total: int
    pagina: int
    tamanho: int
    paginas: int

    @classmethod
    def build[S](cls, page: Page[S], convert: Callable[[S], T]) -> "PageOut[T]":
        items: Sequence[T] = [convert(item) for item in page.items]
        return cls(
            itens=list(items),
            total=page.total,
            pagina=page.request.page,
            tamanho=page.request.size,
            paginas=page.pages,
        )
