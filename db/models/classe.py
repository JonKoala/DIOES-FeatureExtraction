#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import Base

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship, synonym


class Classe(Base):
    __tablename__ = 'Classe'

    id = Column(Integer, primary_key=True)
    nome = Column(String)


    def __repr__(self):
        return '<Classe(id={}, nome={})>'.format(self.id, self.nome)
