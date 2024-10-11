from sqlalchemy.orm import Session
from app.models.node import Node, Connection, Message, MessageCreate


# 创建新节点
def create_node(db: Session, name: str):
    node = Node(name=name, memory="")
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


# 获取所有节点
def get_nodes(db: Session):
    return db.query(Node).all()


def get_node(db: Session, node_id: int):
    return db.query(Node).filter(Node.id == node_id).first()


# 创建新连接
def create_connection(db: Session, source_node_id: int, target_node_id: int):
    connection = Connection(source_node_id=source_node_id, target_node_id=target_node_id)
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def update_node_memory(db: Session, node_id: int, new_memory: str):
    db_node = get_node(db, node_id)
    if db_node:
        db_node.memory = new_memory
        db.commit()
        db.refresh(db_node)
    return db_node


def create_message(db: Session, message: MessageCreate):
    db_message = Message(
        content=message.content,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages_for_node(db: Session, node_id: int, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(
        (Message.sender_id == node_id) | (Message.receiver_id == node_id)
    ).offset(skip).limit(limit).all()