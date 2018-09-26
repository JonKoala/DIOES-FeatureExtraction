#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import Base

from sqlalchemy import Column, Integer, String


class Keyword_Backlisted(Base):
    __tablename__ = 'Keyword_Backlisted'

    id = Column(Integer, primary_key=True)
    palavra = Column(String)


    def __repr__(self):
        return '<Blacklisted(id={}, palavra={})>'.format(self.id, self.palavra)
