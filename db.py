from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from contextlib import contextmanager

class SQLAlchemy:
    def __init__(self, **kwargs):
        self._engine = None
        self._session = None

    def __del__(self):
        self.shutdown()

    def init_app(self, **kwargs):
        """
        DB initialize()
        :param kwargs:
        :return:
        """
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        echo = kwargs.setdefault("DB_ECHO", True)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self._session = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        self.startup()

    def startup(self):
        self._engine.connect()
        logging.info("DB connected.")

    def shutdown(self):
        self._session.close_all()
        self._engine.dispose()
        logging.info("DB disconnected")

    @contextmanager
    def get_db(self):
        if self._session is None:
            raise Exception("must be called 'init_app'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine

sqldb = SQLAlchemy()
