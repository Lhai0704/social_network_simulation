from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 连接 URL：'mysql+pymysql://<username>:<password>@<host>/<database>'
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mysql9898...@localhost/social_network_simulation"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建一个数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建一个基础类，后续模型会继承它
Base = declarative_base()
