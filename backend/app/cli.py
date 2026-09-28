import argparse
import asyncio
import sys
from collections.abc import Sequence

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.application.use_cases import EnsureAdmin
from app.auth.domain.errors import AuthError
from app.auth.infrastructure.password_hasher import Argon2PasswordHasher
from app.auth.infrastructure.user_repository import SqlAlchemyUserRepository
from app.core.config import Settings, get_settings
from app.db.session import enable_sqlite_foreign_keys
from app.db.transaction import SqlAlchemyTransactionManager
from app.movies.infrastructure.seed.loader import SeedLoader


async def _ensure_admin(settings: Settings, email: str, name: str, password: str) -> bool:
    engine = create_async_engine(settings.database_url)
    enable_sqlite_foreign_keys(engine)
    try:
        async with async_sessionmaker(engine, expire_on_commit=False)() as session:
            use_case = EnsureAdmin(
                SqlAlchemyUserRepository(session),
                Argon2PasswordHasher(),
                SqlAlchemyTransactionManager(session),
            )
            return await use_case.execute(email=email, name=name, password=password)
    finally:
        await engine.dispose()


def _seed(args: argparse.Namespace, settings: Settings) -> int:
    engine = create_engine(settings.sync_database_url)
    report = SeedLoader(engine, settings.seed_data_dir).load(reset=args.reset)
    engine.dispose()
    if report.skipped:
        print("Catálogo já populado; carga ignorada (use --reset para recarregar).")
    for table, count in report.inserted.items():
        print(f"{table}: {count} linhas")
    created = asyncio.run(
        _ensure_admin(settings, settings.admin_email, settings.admin_name, settings.admin_password)
    )
    print(f"Administrador {settings.admin_email} {'criado' if created else 'já existente'}.")
    return 0


def _create_admin(args: argparse.Namespace, settings: Settings) -> int:
    created = asyncio.run(_ensure_admin(settings, args.email, args.name, args.password))
    print(f"Administrador {args.email} {'criado' if created else 'já existente'}.")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    commands = parser.add_subparsers(required=True)
    seed = commands.add_parser("seed", help="Carrega os CSVs e cria o administrador padrão")
    seed.add_argument("--reset", action="store_true", help="Apaga os dados antes de carregar")
    seed.set_defaults(handler=_seed)
    admin = commands.add_parser("create-admin", help="Cria um administrador")
    admin.add_argument("--email", required=True)
    admin.add_argument("--name", required=True)
    admin.add_argument("--password", required=True)
    admin.set_defaults(handler=_create_admin)
    return parser


def main(argv: Sequence[str] | None = None, settings: Settings | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        exit_code: int = args.handler(args, settings or get_settings())
    except AuthError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
