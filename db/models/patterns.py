from . import Base

from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Patterns(Base):
    __tablename__ = 'Predicao_Regex_DIOES3'

    DIOES3_id = Column(Integer, ForeignKey('Publicacao.id'), primary_key=True)
    max_valor = Column(Numeric)

    publicacao_id = synonym('DIOES3_id')
    valor = synonym('max_valor')


    def __repr__(self):
        return '<Patterns(publicacao_id={}, valor={})>'.format(self.publicacao_id, self.valor)
