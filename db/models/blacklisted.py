from . import Base

from sqlalchemy import Column, Integer, String


class Blacklisted(Base):
    __tablename__ = 'Backlist_Palavra_DIOES3'

    id = Column(Integer, primary_key=True)
    palavra = Column(String)


    def __repr__(self):
        return '<Blacklisted(id={}, palavra={})>'.format(self.id, self.palavra)
