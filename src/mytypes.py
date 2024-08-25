# vim: set ts=2 sw=2 sts=2 et:
from __future__ import annotations
from typing import List, Dict, Type, Callable, Generator, Self
from typing import Any as any
from dataclasses import dataclass, field, fields

number  = float  | int   #
atom    = number | bool | str # and sometimes "?"
row     = list[atom]
rows    = list[row]
classes = dict[str,rows] # `str` is the class name

def LIST(): return field(default_factory=list)
def DICT(): return field(default_factory=dict) 
