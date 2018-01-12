from . import Base

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Keyword(Base):
    __tablename__ = 'Classe_Keyword_DIOES3'

    id = Column(Integer, primary_key=True)
    classe_id = Column(Integer, ForeignKey('Classe_DIOES3.id'))
    palavra = Column(String)


    def __repr__(self):
        return '<Keyword(id={}, classe_id={}, palavra={})>'.format(self.id, self.classe_id, self.palavra)
