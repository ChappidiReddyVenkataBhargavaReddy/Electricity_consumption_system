import os
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH=os.path.join(BASE_DIR,"database","electricity.db")
SECRET_KEY=os.environ.get("SECRET_KEY","change-this-development-key")
DEFAULT_HIGH_USAGE_THRESHOLD=300.0
