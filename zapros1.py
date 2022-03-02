from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
import datetime
import sqlalchemy
from sqlalchemy import orm

# from werkzeug.security import generate_password_hash, check_password_hash

SqlAlchemyBase = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sqlalchemy.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    # news = orm.relation("News", back_populates='user')

    # def set_password(self, password):
    #     self.hashed_password = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.hashed_password, password)


def user_get():
    db_sess = create_session()
    # user = db_sess.query(User).filter(User.id == 1).first()
    for user in db_sess.query(User).filter(User.address == "module_1", User.speciality.notilike("%engineer%"),
                                           User.position.notilike("%engineer%")).all():
        print(user.id)


if __name__ == '__main__':
    name = input()
    global_init(name)
    # users_add()
    # news_add()
    user_get()
