#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# File name: sample.py
# First Edit: 2020-04-11
# Last Change: 11-Apr-2020.
"""
This scrip is for test

"""
UNKNOWN_URL = 'https://link.springer.com/search/page/{}?package=openaccess&showAll=false&facet-language="En"&facet-content-type="Book"'
MAX_RANGE = 46

for i in range(2, MAX_RANGE + 1):
    print(UNKNOWN_URL.format(i))
