from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime


# class Node(BaseModel):
#     id: int
#     name: str
#     connections: List[int] = []
#     last_message: Optional[str] = None

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    memory = Column(Text)

    # 定义与连接的关系
    connections_from = relationship("Connection", foreign_keys='Connection.source_node_id', back_populates="source_node")
    connections_to = relationship("Connection", foreign_keys='Connection.target_node_id', back_populates="target_node")


# 定义请求体模型
class NodeCreate(BaseModel):
    name: str


# 这是用于返回的模型，包含连接信息
class NodeResponse(BaseModel):
    id: int
    name: str
    connections: List[int] = []

    class Config:
        orm_mode = True
# class NodeCreate(BaseModel):
#     name: str


# class NodeConnection(BaseModel):
#     target_node_id: int

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"))
    target_node_id = Column(Integer, ForeignKey("nodes.id"))

    # 定义连接与节点的关系
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="connections_from")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="connections_to")


class ConnectionCreate(BaseModel):
    target_node_id: int  # 连接到的目标节点 ID


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(1000), index=True)
    sender_id = Column(Integer, ForeignKey("nodes.id"))
    receiver_id = Column(Integer, ForeignKey("nodes.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("Node", foreign_keys=[sender_id])
    receiver = relationship("Node", foreign_keys=[receiver_id])


class MessageBase(BaseModel):
    content: str
    sender_id: int
    receiver_id: int


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
