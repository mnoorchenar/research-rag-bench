import os
from flask import Flask


def create_app():
    server = Flask(__name__, template_folder="../templates", static_folder="../static")
    server.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "rag-bench-dev-secret"),
        DATA_DIR=os.environ.get("DATA_DIR", "data"),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,
    )

    from .routes.ingest import ingest_bp
    from .routes.query import query_bp
    server.register_blueprint(ingest_bp, url_prefix="/api")
    server.register_blueprint(query_bp, url_prefix="/api")

    from .dashboards.eval_dashboard import create_dash_app
    dash_app = create_dash_app(server)

    return server, dash_app
