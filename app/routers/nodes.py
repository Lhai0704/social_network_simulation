import random

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.node import Node, Connection, NodeCreate, NodeResponse, ConnectionCreate, Message, MessageCreate, MessageResponse, Memory
from app.services.ollama_service import generate_message, get_embedding
from database import SessionLocal, engine
from app.services.crud import create_node, get_nodes, create_connection, add_memory, get_node, create_message, get_messages_for_node, get_neighbour
from sqlalchemy.orm import Session
import logging


router = APIRouter()

logger = logging.getLogger(__name__)

nodes: List[Node] = []


# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 添加节点
@router.post("/nodes/", response_model=NodeResponse)
def add_node(node: NodeCreate, db: Session = Depends(get_db)):  # 使用 NodeCreate 作为请求体
    return create_node(db, node.name)


# 获取所有节点
@router.get("/nodes/")
def list_nodes(db: Session = Depends(get_db)):
    return get_nodes(db)


# 获取邻居id列表
def list_neighbour(node_id, db: Session = Depends(get_db)):
    return get_neighbour(db, node_id)


# 创建连接
@router.post("/nodes/{node_id}/connect")
def connect_nodes(node_id: int, target_node_id: ConnectionCreate, db: Session = Depends(get_db)):
    return create_connection(db, node_id, target_node_id.target_node_id)


def generate_memory_based_message(sender_node, receiver_node, db: Session):
    memories = get_relevant_memories(db, sender_node.id)
    memories_text = "\n".join(memories)

    prompt = f"""
    I want you to play a social network user, your name is {sender_node.name}, your profile is as follows:
    ###
    {sender_node.profile}
    ###
    The following is your memory of interaction with other nodes:
    ###
    {memories_text}
    ###
    Based on your profile and memory, discuss the news of Japan's nuclear wastewater discharge with {receiver_node.name}.  His/Her profile is {receiver_node.profile}. 
    This message should imitate the human tone as much as possible, do not explain, just say the content of the message to be sent.
    
    """

    # Generate the message content
    message_content = generate_message(prompt)

    # Update the sender's memory with this interaction
    add_conversation_memory(db, sender_node.id, receiver_node.id, content=message_content)

    return message_content


def add_conversation_memory(db: Session, speaker_id: int, listener_id: int, content: str,
                            context: str = None, sentiment: str = None, importance: float = 0.5):
    # 为说话者添加记忆
    add_memory(db, speaker_id, "conversation", content, True, listener_id, context, sentiment, importance)

    # 为听者添加记忆
    add_memory(db, listener_id, "conversation", content, False, speaker_id, context, sentiment, importance)


@router.post("/messages/", response_model=MessageResponse)
def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    sender_node = get_node(db, message.sender_id)
    receiver_node = get_node(db, message.receiver_id)

    if not sender_node or not receiver_node:
        raise HTTPException(status_code=404, detail="Sender or receiver node not found")

    # Generate message content using memory-based function
    generated_content = generate_memory_based_message(sender_node, receiver_node, db)

    # Create message with generated content
    message.content = generated_content
    return create_message(db, message)


@router.get("/nodes/{node_id}/messages/", response_model=List[MessageResponse])
def get_node_messages(node_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = get_messages_for_node(db, node_id, skip=skip, limit=limit)
    return messages


def conduct_dialogue(node1_id: int, node2_id: int, num_turns: int, db: Session = Depends(get_db)):
    node1 = get_node(db, node1_id)
    node2 = get_node(db, node2_id)

    if not node1 or not node2:
        raise HTTPException(status_code=404, detail="One or both nodes not found")

    dialogue_history = []

    for turn in range(num_turns):
        # Determine sender and receiver for this turn
        sender = node1 if turn % 2 == 0 else node2
        receiver = node2 if turn % 2 == 0 else node1

        # Create a message
        message = MessageCreate(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=""  # Content will be generated by send_message
        )

        # Send the message using the existing send_message function
        sent_message = send_message(message, db)

        dialogue_history.append({
            "turn": turn + 1,
            "sender": sender.name,
            "receiver": receiver.name,
            "content": sent_message.content
        })

        print(f"Turn {turn + 1}: {sender.name} to {receiver.name}: {sent_message.content}")

    return dialogue_history


@router.post("/start-dialogue/")
def start_dialogue(node1_id: int, node2_id: int, num_turns: int = 5, db: Session = Depends(get_db)):
    try:
        dialogue_history = conduct_dialogue(node1_id, node2_id, num_turns, db)
        return {"message": "Dialogue completed", "history": dialogue_history}
    except Exception as e:
        logger.error(f"Error during dialogue: {str(e)}")
        return {"error": "An error occurred during the dialogue", "details": str(e)}


# 获取相关记忆
def get_relevant_memories(db: Session, node_id: int, limit: int = 10) -> List[str]:
    memories = db.query(Memory).filter(Memory.node_id == node_id) \
        .order_by(Memory.importance.desc(), Memory.created_at.asc()) \
        .limit(limit) \
        .all()

    formatted_memories = []
    for memory in memories:
        if memory.is_own_message:
            speaker = "I told " + get_node(db, memory.other_node_id).name
        else:
            speaker = get_node(db, memory.other_node_id).name + " told me"

        formatted_memory = f"{memory.memory_type.upper()} - {speaker}: {memory.content}"
        if memory.context:
            formatted_memory += f" (Context: {memory.context})"
        formatted_memories.append(formatted_memory)

    return formatted_memories


@router.post("/multi-dialogue/")
def multi_dialogue(num_turns: int = 1, db: Session = Depends(get_db)):
    for _ in range(num_turns):
        for node in list_nodes(db):
            neighbours = list_neighbour(node.id, db)
            if neighbours:
                neighbour = random.choice(neighbours)
                conduct_dialogue(node.id, neighbour[0], 1, db)
