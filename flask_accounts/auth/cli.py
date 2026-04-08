import click
from flask import current_app
from .db_init import bootstrap_database, init_schema


def register_cli_commands(app):

    @app.cli.command("auth-bootstrap-db")
    @click.option("--admin-user", prompt=True, help="Postgres admin user")
    @click.option("--admin-db", default="postgres", show_default=True)
    @click.option(
        "--admin-password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=False,
    )
    def auth_bootstrap_db(admin_user, admin_db, admin_password):
        """Create DB + user + schema (requires admin credentials)."""

        bootstrap_database(
            current_app,
            admin_user=admin_user,
            admin_password=admin_password,
            admin_db=admin_db,
        )

        init_schema(current_app)

        click.echo("✔ Database and schema are ready.")

    @app.cli.command("auth-init-db")
    def auth_init_db():
        """Create auth tables/schema in an existing database."""
        init_schema(current_app)
        click.echo("Auth schema initialized.")