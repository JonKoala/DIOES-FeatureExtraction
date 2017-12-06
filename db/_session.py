from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker


class Session:

    def __init__(self, engine, **kwargs):
        self.initializer = sessionmaker(bind=engine, **kwargs)

    # Provide a transactional scope around a series of operations
    @contextmanager
    def start(self):
        session = self.initializer()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
