import os

suffix = os.getenv("SUFFIX", "")
DEVELOPMENT = os.getenv("DEVELOPMENT", "true").strip().lower() == "true"
