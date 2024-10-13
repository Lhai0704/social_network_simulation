from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum, Boolean, JSON
from datetime import datetime


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    profile = Column(JSON)

    # 明确指定 backref 和 foreign_keys
    memories = relationship("Memory", back_populates="node", foreign_keys="Memory.node_id")
    received_messages = relationship("Memory", back_populates="other_node", foreign_keys="Memory.other_node_id")

    # 定义与连接的关系
    connections_from = relationship("Connection", foreign_keys='Connection.source_node_id', back_populates="source_node")
    connections_to = relationship("Connection", foreign_keys='Connection.target_node_id', back_populates="target_node")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    memory_type = Column(Enum("conversation", "fact", "experience", "trait", "relationship"))
    content = Column(Text)
    is_own_message = Column(Boolean)
    other_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    context = Column(Text, nullable=True)
    sentiment = Column(Enum("positive", "neutral", "negative"), nullable=True)
    importance = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), onupdate=func.now())

    # 明确指定 foreign_keys
    node = relationship("Node", back_populates="memories", foreign_keys=[node_id])
    other_node = relationship("Node", back_populates="received_messages", foreign_keys=[other_node_id])


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"))
    target_node_id = Column(Integer, ForeignKey("nodes.id"))

    # 定义连接与节点的关系
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="connections_from")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="connections_to")


# 定义请求体模型
class NodeCreate(BaseModel):
    name: str


# 这是用于返回的模型，包含连接信息
class NodeResponse(BaseModel):
    id: int
    name: str
    connections: List[int] = []

    class Config:
        from_attributes = True


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
        from_attributes = True
