# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_test.ipynb (unless otherwise specified).

__all__ = ['get_all_flags', 'get_cell_flags', 'NoExportPreprocessor', 'test_nb']

# Cell
from .imports import *
from .sync import *
from .export import *
from .export import _mk_flag_re
from .export2html import _re_notebook2script

from nbconvert.preprocessors import ExecutePreprocessor

# Cell
_re_all_flag = ReTstFlags(True)

# Cell
def get_all_flags(cells):
    "Check for all test flags in `cells`"
    if len(Config().get('tst_flags',''))==0: return []
    result = []
    for cell in cells:
        if cell['cell_type'] == 'code': result.extend(_re_all_flag.findall(cell['source']))
    return set(result)

# Cell
_re_flags = ReTstFlags(False)

# Cell
def get_cell_flags(cell):
    "Check for any special test flag in `cell`"
    if cell['cell_type'] != 'code' or len(Config().get('tst_flags',''))==0: return []
    return _re_flags.findall(cell['source'])

# Cell
class NoExportPreprocessor(ExecutePreprocessor):
    "An `ExecutePreprocessor` that executes cells that don't have a flag in `flags`"
    def __init__(self, flags, **kwargs):
        self.flags = flags
        super().__init__(**kwargs)

    def preprocess_cell(self, cell, resources, index):
        if 'source' not in cell or cell['cell_type'] != "code": return cell, resources
        for f in get_cell_flags(cell):
            if f not in self.flags: return cell, resources
        if check_re(cell, _re_notebook2script): return cell, resources
        return super().preprocess_cell(cell, resources, index)

# Cell
def test_nb(fn, flags=None):
    "Execute tests in notebook in `fn` with `flags`"
    os.environ["IN_TEST"] = '1'
    if flags is None: flags = []
    try:
        nb = read_nb(fn)
        nb = call_cb('begin_test_nb', nb, fn, flags)
        for f in get_all_flags(nb['cells']):
            if f not in flags: return
        ep = NoExportPreprocessor(flags, timeout=600, kernel_name='python3')
        pnb = nbformat.from_dict(nb)
        ep.preprocess(pnb)
        nb = call_cb('after_test_nb', fn)
    finally: os.environ.pop("IN_TEST")