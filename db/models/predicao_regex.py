from . import Base

from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Predicao_Regex(Base):
    __tablename__ = 'Predicao_Regex'

    publicacao_id = Column(Integer, ForeignKey('Publicacao.id'), primary_key=True)
    max_valor = Column(Numeric)

    valor = synonym('max_valor')


    def __repr__(self):
        return '<Regex_Pattern(publicacao_id={}, valor={})>'.format(self.publicacao_id, self.valor)
