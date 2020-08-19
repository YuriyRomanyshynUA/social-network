from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL


class Database:

    def __init__(self, app=None):
        if app is not None:
            self._init_database(app)

    def _init_database(self, app):
        self._app = app
        self._database_uri = URL(
            app.config["DATABASE"]["DRIVER"],
            app.config["DATABASE"]["USER"],
            app.config["DATABASE"]["PASSWORD"],
            app.config["DATABASE"]["HOST"],
            None,
            app.config["DATABASE"]["NAME"]
        )
        self._engine = create_engine(self._database_uri)
        self._session_factory = scoped_session(sessionmaker(self._engine))

        @app.teardown_appcontext
        def on_request_context_teardown(*args, **kwargs):
            self._session_factory.remove()

    def init_app(self, app):
        self._init_database(app)

    @property
    def session(self):
        if not hasattr(self, "_session_factory"):
            raise Exception("Database is not init")
        return self._session_factory()
