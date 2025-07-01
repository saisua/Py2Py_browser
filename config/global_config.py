import os

suffix = os.getenv("P2Py_SUFFIX", "")
DEVELOPMENT = os.getenv("P2Py_DEVELOPMENT", "true").strip().lower() == "true"
