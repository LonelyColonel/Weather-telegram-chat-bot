import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception('Необходимо указать файл базы данных')
    connect_string = f'mysql+mysqlconnector://{db_file.strip()}'
    print(f'Подключение к базе данных по адресу {connect_string}')

    engine = sa.create_engine(connect_string, echo=False)

    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory

    return __factory()
