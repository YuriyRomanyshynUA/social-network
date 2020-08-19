import json
from logging.config import dictConfig as loadLogginConfig
from pydantic import ValidationError
from email_validator import EmailNotValidError
from flask import Flask
from flask_cors import CORS
#
from social_network.errors import ApplicationError
from social_network.database import Database
from social_network.settings import Config


__all__ = ["create_application"]


db = Database()


def create_application():
    app = Flask("social_network")
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    setup_logging(app)
    register_error_handlers(app)
    register_blueprints(app)

    return app


def setup_logging(app):
    with open(app.config["LOGGING_SETTINGS"], "r") as f:
        loadLogginConfig(json.load(f))


def register_blueprints(app):
    from social_network.blueprints import auth_blueprint
    from social_network.blueprints import posts_blueprint
    from social_network.blueprints import users_blueprint
    from social_network.blueprints import analytics_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(posts_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(analytics_blueprint)


def register_error_handlers(app):

    def _handle_error(error):
        reason_tmp = getattr(error, "description",  "Internal error")
        code_tmp = getattr(error, "code",  500)
        details_tmp = getattr(error, "details",  [])

        reason = reason_tmp if isinstance(reason_tmp, str) else "Internal error"
        code = int(code_tmp) if isinstance(code_tmp, int) else 500
        details = details_tmp if isinstance(details_tmp, (list, tuple)) else []

        return {
            "status": "error",
            "reason": reason,
            "details": details
        }, code

    def default_handler(error):
        app.logger.exception(f"Error occurred:\n{str(error)}")
        return _handle_error(error)


    def application_error_handler(error):
        app.logger.error(f"Error occurred:\n{str(error)}")
        return _handle_error(error)
        
    def validation_error_handler(error):
        app.logger.info(f"Invalid input:\n{str(error)}")
        return {
            "status": "error",
            "reason": "Incorrec input",
            "details": error.errors()
        }, 400

    def unvalid_email_error_handler(error):
        app.logger.info(f"Invalid Email:\n{str(error)}")
        return {
            "status": "error",
            "reason": "Email is not valid",
            "details": []
        }, 400
        
    app.register_error_handler(Exception, default_handler)
    app.register_error_handler(ValidationError, validation_error_handler)
    app.register_error_handler(ApplicationError, application_error_handler)
    app.register_error_handler(EmailNotValidError, unvalid_email_error_handler)
