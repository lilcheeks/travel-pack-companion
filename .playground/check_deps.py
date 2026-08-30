import sys
print("python:", sys.executable, sys.version)
try:
    import flask
    print("flask:", flask.__version__)
except ImportError as e:
    print("flask NOT available:", e)
try:
    import jinja2
    print("jinja2:", jinja2.__version__)
except ImportError as e:
    print("jinja2 NOT available:", e)
