from . import Base

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Predicao(Base):
    __tablename__ = 'Predicao_Classificacao_DIOES3'

    DIOES3_id = Column(Integer, ForeignKey('Publicacao.id'), primary_key=True)
    classe_id = Column(Integer, ForeignKey('Classe_DIOES3.id'))

    publicacao_id = synonym('DIOES3_id')

    publicacao = relationship('Publicacao', uselist=False)


    def __repr__(self):
        return '<Predicao(publicacao_id={}, classe_id={})>'.format(self.publicacao_id, self.classe_id)
