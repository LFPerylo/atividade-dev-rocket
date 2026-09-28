from pathlib import Path

from sqlalchemy import create_engine, text

from app.cli import main
from app.core.config import Settings
from tests.integration.seed.sample_data import write_sample_data


def make_settings(database_path: Path, data_dir: Path) -> Settings:
    return Settings(
        database_url=f"sqlite+aiosqlite:///{database_path}",
        seed_data_dir=data_dir,
        admin_email="admin@rocketlab.dev",
        admin_password="s3nha-forte",
        admin_name="Admin",
    )


def scalar(database_path: Path, sql: str) -> object:
    with create_engine(f"sqlite:///{database_path}").connect() as connection:
        return connection.execute(text(sql)).scalar_one()


def test_seed_command_loads_data_and_creates_default_admin(
    database_path: Path, tmp_path: Path
) -> None:
    settings = make_settings(database_path, write_sample_data(tmp_path / "seed"))

    exit_code = main(["seed"], settings)

    assert exit_code == 0
    assert scalar(database_path, "SELECT COUNT(*) FROM dim_movies") == 2
    admin_email = scalar(database_path, "SELECT email FROM users WHERE papel = 'admin'")
    assert admin_email == "admin@rocketlab.dev"


def test_create_admin_command_adds_admin(database_path: Path, tmp_path: Path) -> None:
    settings = make_settings(database_path, tmp_path)

    exit_code = main(
        [
            "create-admin",
            "--email",
            "outra@rocketlab.dev",
            "--name",
            "Outra",
            "--password",
            "12345678",
        ],
        settings,
    )

    assert exit_code == 0
    assert scalar(database_path, "SELECT name FROM users") == "Outra"


def test_create_admin_command_fails_for_invalid_data(database_path: Path, tmp_path: Path) -> None:
    settings = make_settings(database_path, tmp_path)

    exit_code = main(
        ["create-admin", "--email", "invalido", "--name", "X", "--password", "12345678"], settings
    )

    assert exit_code == 1
