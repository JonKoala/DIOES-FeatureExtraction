#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def _is_integer(val):
    try:
        int(val)
        return True
    except ValueError:
        return False

def _is_float(val):
    try:
        float(val)
        return not _is_integer(val)
    except ValueError:
        return False

def _is_bool(val):
    return str.casefold(val) == 'true' or str.casefold(val) == 'false'

def _is_null(val):
    return str.casefold(val) == 'null' or str.casefold(val) == 'none'

def _parse_val(val):
    if _is_integer(val):
        return int(val)
    if _is_float(val):
        return float(val)
    if _is_bool(val):
        return str.casefold(val) == 'true'
    if _is_null(val):
        return None
    return val

def get_tunning_params():
    param_prefix = 'DIARIOBOT_DM_PARAM_'
    len_prefix = len(param_prefix)

    params = {}
    gen = (key for key in os.environ.keys() if key.startswith(param_prefix))
    for key in gen:
        parsed_key = str.casefold(key[len_prefix:])
        params[parsed_key] =_parse_val(os.environ[key])

    return params
