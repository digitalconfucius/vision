"""Flask app factory."""
from flask import Flask

from . import config, db, filters, indexer, routes


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["WIKI_DIR"] = str(config.WIKI_DIR)
    app.config["DB_PATH"] = str(config.DB_PATH)
    app.secret_key = "vision-local-dev"  # local-only app, no sensitive sessions

    # Ensure wiki dir exists
    config.WIKI_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database schema
    db.init_db()

    # Initial full index so first request is fast
    indexer.reindex_all()

    # Register filters and routes
    filters.register(app)
    app.register_blueprint(routes.bp)

    # Close db connection at end of each request
    app.teardown_appcontext(db.close_connection)

    return app
