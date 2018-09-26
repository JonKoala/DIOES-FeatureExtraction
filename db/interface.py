#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import _connection as connection
from ._session import Session


class Dbinterface:

    def __init__(self, connectionstring, **kwargs):
        self.engine = connection.connect(connectionstring)
        self.session = Session(self.engine, **kwargs)

    def opensession(self):
        return self.session.start()
