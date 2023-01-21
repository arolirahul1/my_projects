# -*- coding: utf-8 -*-
import tempfile
import os
from pathlib import Path
def getTempfile(suffix=''):
    filename = tempfile.TemporaryFile(suffix=suffix).name
    Path(filename).touch()
    return filename

def getNamedTempFile(filename, touch=True):
    f = tempfile.gettempdir()
    f = os.path.join(f, filename)
    if touch:
        Path(f).touch()
    return f