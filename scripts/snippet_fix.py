"""Import shim: snippet-fix.py has a hyphen, so sibling scripts import it here."""
import importlib.util, pathlib
_p = pathlib.Path(__file__).with_name("snippet-fix.py")
_s = importlib.util.spec_from_file_location("snippet_fix_impl", _p)
_m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
apply = _m.apply
set_meta = _m.set_meta
