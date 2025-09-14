import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from pathlib import Path

from elasticsearch import Elasticsearch
from flask import Flask, current_app, request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = _l("Please sign in to access this page.")
mail = Mail()
moment = Moment()
babel = Babel()


def get_locale() -> None:
    """Determine the best match with our supported languages."""
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])


def create_app(config_class=Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialization of extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    app.elasticsearch = (
        Elasticsearch([app.config["ELASTICSEARCH_URL"]])
        if app.config["ELASTICSEARCH_URL"]
        else None
    )

    # Registration of blueprints.
    from app.errors import bp as errors_bp  # noqa: E402

    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp  # noqa: E402

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp  # noqa: E402

    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp

    app.register_blueprint(cli_bp)

    # Logging configuration.
    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])

            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                toaddrs=app.config["ADMINS"],
                subject="Microblog Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not Path("logs").exists():
            Path("logs").mkdir()

        file_handler = RotatingFileHandler(
            "logs/microblog.log",
            maxBytes=10240,
            backupCount=10,
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Microblog startup")

    return app


from app import models  # noqa: E402, F401
