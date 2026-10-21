"""Chooses which implementation the tests import.

    python3 -m unittest -v                         # tests YOUR code in starter/
    LLD_TARGET=solution python3 -m unittest -v     # tests the sample solution
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TARGET = os.environ.get("LLD_TARGET", "starter")
sys.path.insert(0, os.path.join(_ROOT, _TARGET))
