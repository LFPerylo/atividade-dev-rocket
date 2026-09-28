import gzip
from pathlib import Path

SAMPLE_FILES = {
    "dim_genres.csv.gz": "nome_genero,sk_genre_id\nDrama,g-drama\nCrime,g-crime\n",
    "dim_companies.csv.gz": "nome_produtora,sk_company_id\nO2 Filmes,c-o2\n",
    "dim_people.csv.gz": (
        "nome_pessoa,tipo_pessoa,sk_person_id\n"
        "Fernando Meirelles,Diretor,p-fm\n"
        "Alice Braga,Ator,p-ab\n"
        '"Kátia """"K"""" Lund",Diretor,p-kl\n'
        '"Kátia """"K"""" Lund""",Diretor,p-kl-dup\n'
    ),
    "dim_movies.csv.gz": (
        "sk_movie_id,id_filme,titulo,data_lancamento,ano_lancamento,duracao_minutos,"
        "status_filme,sinopse,url_poster,url_backdrop\n"
        'm-cdd,598,Cidade de Deus,2002-08-30,2002,130,Lançado,"""Buscapé"" ""cresce"".""",,\n'
        "m-blind,1,Ensaio sobre a Cegueira,2008-09-12,2008,0,Lançado,,,\n"
    ),
    "bridge_movie_genre.csv.gz": (
        "sk_movie_id,sk_genre_id\nm-cdd,g-drama\nm-cdd,g-crime\nm-blind,g-drama\n"
    ),
    "bridge_movie_company.csv.gz": "sk_movie_id,sk_company_id\nm-cdd,c-o2\n",
    "bridge_movie_person.csv.gz": (
        "sk_movie_id,sk_person_id\nm-cdd,p-fm\nm-blind,p-fm\nm-blind,p-ab\n"
        "m-cdd,p-kl\nm-cdd,p-kl-dup\nm-blind,p-kl-dup\n"
    ),
    "fact_movies_performance.csv.gz": (
        "sk_movie_id,orcamento_usd,receita_usd,lucro_usd,orcamento_brl,receita_brl,lucro_brl,"
        "popularidade,nota_tmdb,qtd_tmdb,nota_imdb,qtd_imdb\n"
        "m-cdd,3300000.0,30641770.0,27341770.0,,,0.0,40.5,8.4,7000.0,8.6,800000.0\n"
    ),
    "dim_reviews.csv.gz": (
        "sk_review_id,sk_movie_id,qtd_avaliacoes_usuarios,nota_media_usuarios\n"
        "m-cdd,m-cdd,2,9.0\n"
        "m-blind,m-blind,0,\n"
    ),
    "movies_reviews.csv.gz": (
        "sk_movie_review_id,sk_movie_id,nome,nota,comentario\n"
        "r1,m-cdd,Ana,10.0,Obra-prima.\n"
        "r2,m-cdd,Bruno,8.0,Muito bom.\n"
        "r3,m-blind,Carla,6.0,Interessante.\n"
    ),
}


def write_sample_data(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in SAMPLE_FILES.items():
        with gzip.open(directory / name, "wt", encoding="utf-8") as file:
            file.write(content)
    return directory
