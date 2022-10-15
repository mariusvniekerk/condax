import sys

if sys.version_info < (3, 8):
    from importlib_metadata import version
else:
    from importlib.metadata import version

try:
    __version__ = version(__package__)
except Exception:
    __version__ = "unknown"
