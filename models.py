from sqlalchemy import Column, Integer, Table, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
metadata = Base.metadata

WinesRegion = Table(
    'wines_region', metadata,
    Column('wine_id', Integer, ForeignKey('wines.id'), nullable=False),
    Column('region_id', Integer, ForeignKey('regions.id'), nullable=False)
)

WinesUser = Table(
    'wines_user', metadata,
    Column('wine_id', Integer, ForeignKey('wines.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)


class Regions(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Wines(Base):
    __tablename__ = 'wines'

    id = Column(Integer, primary_key=True)
    variety = Column(Text)
    description = Column(Text)
    points = Column(Integer)
    price = Column(Integer)
    winery = Column(Text)
    country = Column(Text)
    province = Column(Text)

    users = relationship('User', secondary=WinesUser, backref=backref('wines', lazy='dynamic'))
    regions = relationship('Regions', secondary=WinesRegion, backref=backref('regions', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'variety': self.variety,
            'description': self.description,
            'points': self.points,
            'price': self.price,
            'winery': self.winery,
            'country': self.country,
            'province': self.province,
            'regions': [region.name for region in self.regions]
        }


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    username = Column(Text, unique=True)
    password = Column(Text)
    email = Column(Text, unique=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @staticmethod
    def create(db_session, name, username, password, email):
        user = User(name=name, username=username, password=password, email=email)
        db_session.add(user)
        db_session.flush()
        db_session.commit()
        db_session.refresh(user)
        return user
