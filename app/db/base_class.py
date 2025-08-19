from sqlalchemy.orm import declarative_base

# This file should only define the Base. Models should import Base from here.
# Importing models into this file creates critical circular dependencies.

Base = declarative_base()
