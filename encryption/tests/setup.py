import os

os.environ["P2Py_DB_URL"] = \
	f"encryption/tests/test{os.environ.get("P2Py_SUFFIX")}.db"
