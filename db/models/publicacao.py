from . import Base

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, synonym

class Publicacao(Base):
    __tablename__ = 'Results_Crowdsourcer_DIOES3'

    publicacao_id = Column(Integer, ForeignKey('DIOES3.id'), primary_key=True)
    classe_id = Column(Integer, ForeignKey('Classe_DIOES3.id'))
    publicacao = Column(String)
    tipo_publicacao = Column(String)
    dt_publicacao = Column(String)
    classe = Column(String)

    id = synonym('publicacao_id')
    tipo = synonym('tipo_publicacao')
    texto = synonym('publicacao')


    def __repr__(self):
        return '<Publicacao(id={}, tipo={}, data={}, classe={})>'.format(self.publicacao_id, self.tipo, self.dt_publicacao, self.classe)
