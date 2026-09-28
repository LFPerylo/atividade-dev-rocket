# Claquete — Sistema de Avaliação de Filmes

Catálogo de filmes inspirado no Letterboxd, desenvolvido para a Atividade DEV do **RocketLab 2026 (Visagio)**.
O Administrador navega por mais de 95 mil filmes, busca e filtra o catálogo, consulta detalhes completos e o
histórico de avaliações, gerencia o catálogo (cadastrar, editar, remover) e publica notas de 1 a 5 estrelas
com resenhas.

| Stack | |
|---|---|
| Frontend | Vite, React 19, TypeScript, React Router, TanStack Query, react-hook-form + zod, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, JWT (PyJWT), argon2 (pwdlib) |
| Banco | SQLite |
| Qualidade | pytest, Vitest + Testing Library + MSW, Playwright, Storybook, ruff, mypy, oxlint, Prettier |
| DevOps | Docker, docker-compose, nginx, GitHub Actions, Dependabot |

## Funcionalidades

| Requisito | Onde está |
|---|---|
| Cadastrar filmes (título, diretor, ano, gênero, sinopse…) | `Adicionar filme` no catálogo → `POST /api/v1/movies` |
| Catálogo paginado | Página inicial, 24 filmes por página → `GET /api/v1/movies?pagina=` |
| Detalhes do filme com avaliações | `/filmes/:id` → `GET /api/v1/movies/{id}` e `/reviews` |
| Barra de pesquisa | Busca por título **ou diretor**, com debounce e estado na URL |
| Atualizar e remover filmes | Botões `Editar` / `Remover` (com confirmação) nos detalhes |
| Nova avaliação (1–5 estrelas + resenha) | Formulário com meias estrelas nos detalhes |
| Média das avaliações | Exibida em cada card e no resumo da página de detalhes |

Extras: autenticação do administrador (JWT), filtros por gênero, ano e nota mínima, ordenação por popularidade,
média, título ou ano, layout responsivo, cache de consultas no cliente (TanStack Query), Storybook, testes
automatizados (unitários, integração, API, componentes e E2E), Docker e CI.

## Como executar

### Opção 1 — Docker (mais simples)

Requer Docker. Na raiz do projeto:

```bash
docker compose up --build
```

Acesse **http://localhost:8080**. Na primeira subida o backend aplica as migrations e carrega os CSVs
(cerca de 30 segundos). Os dados ficam no volume `claquete-data`.

### Opção 2 — Ambiente local

Requer Python 3.12+, [uv](https://docs.astral.sh/uv/) e Node.js 22+.

```bash
make setup   # instala dependências, cria backend/.env, aplica migrations e carrega os dados
make dev     # API em http://localhost:8000 e frontend em http://localhost:5173
```

<details>
<summary>Sem <code>make</code> (passo a passo manual)</summary>

```bash
cd backend
cp .env.example .env
uv sync --extra dev
uv run alembic upgrade head
uv run python -m app.cli seed
uv run uvicorn app.main:app --reload --port 8000
```

Em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

</details>

### Acesso de administrador

Leitura é pública. Para cadastrar, editar, remover e avaliar, clique em **Entrar**:

- E-mail: `admin@rocketlab.dev`
- Senha: `rocketlab2026`

As credenciais iniciais vêm de `ADMIN_EMAIL` / `ADMIN_PASSWORD` (`backend/.env` ou variáveis do compose).
Outros administradores podem ser criados com:

```bash
cd backend && uv run python -m app.cli create-admin --email voce@exemplo.com --name "Seu Nome" --password "senha-segura"
```

Em produção, defina `JWT_SECRET_KEY` com um valor longo e aleatório.

## Testes e qualidade

```bash
make test        # pytest com cobertura + Vitest com cobertura
make lint        # ruff, mypy (strict), oxlint, tsc e Prettier
make e2e         # Playwright: sobe API e frontend com banco dedicado e roda os fluxos ponta a ponta
make storybook   # catálogo de componentes em http://localhost:6006
```

- **Backend:** 160+ testes — domínio puro, casos de uso com fakes, repositórios e carga de dados em SQLite
  migrado pelo Alembic, API via `httpx`, e um teste que garante que as migrations estão sincronizadas com os modelos.
- **Frontend:** 80+ testes com Testing Library e MSW cobrindo domínio, cliente HTTP, componentes e páginas.
- **E2E:** busca, filtros, rota protegida, login e o ciclo completo do administrador (cadastrar → avaliar →
  editar → remover) em desktop e mobile.

O pipeline do GitHub Actions (`.github/workflows/ci.yml`) roda lint, tipos, testes, build, Storybook, E2E e
build das imagens Docker a cada push e pull request.

## Arquitetura

```text
.
├── backend/
│   ├── app/
│   │   ├── movies/
│   │   │   ├── domain/          entidades, regras (estrelas, filtros, paginação), erros e ports
│   │   │   ├── application/     casos de uso (listar, detalhar, cadastrar, editar, remover, avaliar)
│   │   │   ├── infrastructure/  repositórios SQLAlchemy, mapeadores e carga dos CSVs
│   │   │   └── models.py        modelo ORM (esquema estrela da base)
│   │   ├── auth/                mesmo desenho: domínio, casos de uso, JWT, argon2 e repositório
│   │   ├── api/v1/              rotas FastAPI, schemas e tradução de erros de domínio para HTTP
│   │   └── cli.py               seed e create-admin
│   ├── data/seed/               CSVs compactados (.csv.gz)
│   ├── migrations/              Alembic (schema, administradores, índices de ordenação)
│   └── tests/                   unit, integration e api
├── frontend/
│   ├── src/
│   │   ├── domain/              tipos, escala de estrelas, filtros ↔ URL, formatação
│   │   ├── infrastructure/      cliente HTTP e armazenamento do token
│   │   ├── features/            auth, movies e reviews (hooks de API, componentes e páginas)
│   │   ├── shared/ui/           componentes reutilizáveis com stories
│   │   └── app/                 rotas, layout e providers
│   └── e2e/                     Playwright
├── docker-compose.yml
└── Makefile
```

O backend segue Clean Architecture: `domain` não depende de framework, `application` conhece apenas os ports
(Protocols) e `infrastructure`/`api` são adaptadores. O frontend segue a mesma ideia: regras puras em `domain`,
I/O em `infrastructure` e UI organizada por feature.

### API

Documentação interativa em `http://localhost:8000/docs`.

| Método | Rota | Autenticação |
|---|---|---|
| `POST` | `/api/v1/auth/login` | – |
| `GET` | `/api/v1/auth/me` | Bearer |
| `GET` | `/api/v1/movies?pagina&tamanho&busca&genero&ano_de&ano_ate&estrelas_min&ordenar&ordem` | – |
| `GET` | `/api/v1/movies/{id}` | – |
| `POST` | `/api/v1/movies` | Bearer |
| `PUT` | `/api/v1/movies/{id}` | Bearer |
| `DELETE` | `/api/v1/movies/{id}` | Bearer |
| `GET` | `/api/v1/movies/{id}/reviews?pagina&tamanho` | – |
| `POST` | `/api/v1/movies/{id}/reviews` | Bearer |
| `GET` | `/api/v1/genres` | – |

## Decisões de projeto

- **Escala de notas.** Os dados trazem notas de 0 a 10; o requisito pede 1 a 5 estrelas. O banco continua em
  0–10 e a interface trabalha com meias estrelas (1; 1,5; …; 5), com `nota = estrelas × 2`. Avaliações
  históricas aparecem convertidas (9,8 → 4,9★).
- **Dados como gabarito.** Os CSVs são a referência oficial e são carregados exatamente como vieram: a carga
  só converte células vazias em nulo e textos em datas/números. Nomes, sinopses, durações `0` e o resumo
  `dim_reviews.csv` são preservados, e as contagens do banco batem linha a linha com os arquivos.
- **Média das avaliações.** A média exibida vem de `dim_reviews` (gabarito). Cada avaliação publicada pelo
  administrador entra nesse resumo de forma incremental, na mesma transação:
  `nova média = (média × quantidade + nota) ÷ (quantidade + 1)`. Um filme sem resumo começa pela própria nota.
  Assim o gabarito nunca é sobrescrito por recálculo, e ordenar ou filtrar por média não exige agregar 95 mil filmes.
- **Dados versionados.** Os CSVs (~222 MB) ficam compactados em `backend/data/seed/*.csv.gz` (~115 MB), abaixo do
  limite de arquivo do GitHub, e o seed lê gzip diretamente.
- **Segurança.** Senhas com argon2, JWT com expiração, login com tempo constante (não revela e-mails
  cadastrados), escrita restrita ao administrador e busca com curingas do `LIKE` escapados.
