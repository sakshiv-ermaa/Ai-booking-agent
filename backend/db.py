from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./conversation.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    session_id = Column(String, primary_key=True, index=True)
    user_input = Column(String, default="")
    intent = Column(String, default="")
    date = Column(String, default="")
    time = Column(String, default="")
    response = Column(String, default="")
    suggested_time = Column(String, default="")
    awaiting_confirmation = Column(Boolean, default=False)
    greeted = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
