from background.config import BaseConfig
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table,DateTime
from sqlalchemy.ext.automap import automap_base

Bases = automap_base()
Session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=BaseConfig.engine))
Base = declarative_base()
Base.query = Session.query_property()
session = Session()





user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey(
                       'users.id'), primary_key=True),
                   Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True), extend_existing=True)


class User(Base):
    """
    Tabela z kontami użytkowników::

        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        username = Column(String(25), unique=True, nullable=False)
        password = Column(String(), nullable=False)
        deleted = Column(Boolean(), default= "False")
        roles = relationship('roles', secondary=user_roles , back_populates='users')

        def __init__(self, username, password,deleted):
            self.username = username
            self.password = password
            self.deleted = deleted
            self.authenticated = True

    """

    __tablename__ = "users"
    # __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    deleted = Column(Boolean(), default="False")
    roles = relationship('roles', secondary=user_roles, back_populates='users')

    # first_name, last_name,
    def __init__(self, id, username, password, deleted):
        self.id = id
        # self.first_name = first_name
        # self.last_name = last_name
        self.username = username
        self.password = password
        self.deleted = deleted

class roles(Base):
    """
    Tabela z rolami::

        __tablename__ = 'roles'
        id = Column(Integer(), primary_key=True)
        role = Column(String(50), unique=True)
        users = relationship('User', secondary=user_roles, back_populates='roles')

        def __init__(self, role):
            self.role = role

    """
    __tablename__ = 'roles'
   # __table_args__ = {'extend_existing': True}
    id = Column(Integer(), primary_key=True)
    role = Column(String(50), unique=True)
    users = relationship('User', secondary=user_roles, back_populates='roles')

    def __init__(self, role):
        self.role = role



class JWTTokenBlocklist(Base):
    """
    Tabela do blokowania tokenów które jeszcze nie straciły ważności::

    """
    __tablename__ = "jwt_token_block_list"
    id = Column(Integer, primary_key=True)
    jwt_token = Column(String, nullable=False)
    created_at = Column(DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

 

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    id_user = Column(Integer, ForeignKey('users.id'), nullable=False)

class UserCourse(Base):
    __tablename__ = "user_courses"
    id_user = Column(Integer, ForeignKey('users.id'),primary_key=True, nullable=False)
    id_course = Column(Integer, ForeignKey('courses.id'), nullable=False)
    user = relationship('User', backref='user_courses')
    course = relationship('Course', backref='user_courses')


Bases.prepare()