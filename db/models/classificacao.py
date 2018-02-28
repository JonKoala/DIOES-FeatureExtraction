from . import Base

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Classificacao(Base):
    __tablename__ = 'Classificacao'

    publicacao_id = Column(Integer, ForeignKey('Publicacao.id'), primary_key=True)
    classe_id = Column(Integer, ForeignKey('Classe.id'))

    publicacao = relationship('Publicacao', uselist=False)


    def __repr__(self):
        return '<Classificacao(publicacao_id={}, classe_id={})>'.format(self.publicacao_id, self.classe_id)
