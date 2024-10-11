from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.node import Node, Connection, NodeCreate, NodeResponse, ConnectionCreate, Message, MessageCreate, MessageResponse
from app.services.ollama_service import generate_message, get_embedding
from database import SessionLocal, engine
from app.services.crud import create_node, get_nodes, create_connection, update_node_memory, get_node, create_message, get_messages_for_node
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


# curl -X POST "http://localhost:8000/nodes/" -H "Content-Type: application/json" -d '{"name": "Amy"}'
# @router.post("/nodes/", response_model=Node)
# async def create_node(node: NodeCreate):
#     new_node = Node(id=len(nodes) + 1, name=node.name)
#     nodes.append(new_node)
#     return new_node

# 添加节点
# curl -X POST "http://localhost:8000/nodes/" -H "Content-Type: application/json" -d '{"name": "Amy"}'
@router.post("/nodes/", response_model=NodeResponse)
def add_node(node: NodeCreate, db: Session = Depends(get_db)):  # 使用 NodeCreate 作为请求体
    return create_node(db, node.name)


# # curl "http://localhost:8000/nodes/"
# @router.get("/nodes/", response_model=List[Node])
# async def read_nodes():
#     return nodes

# 获取所有节点
@router.get("/nodes/")
def list_nodes(db: Session = Depends(get_db)):
    return get_nodes(db)


# curl "http://localhost:8000/nodes/1"
# @router.get("/nodes/{node_id}", response_model=Node)
# async def read_node(node_id: int):
#     for node in nodes:
#         if node.id == node_id:
#             return node
#     raise HTTPException(status_code=404, detail="Node not found")


# curl -X POST "http://localhost:8000/nodes/1/generate_message"
# @router.post("/nodes/{node_id}/generate_message")
# async def generate_node_message(node_id: int):
#     node = next((n for n in nodes if n.id == node_id), None)
#     if not node:
#         raise HTTPException(status_code=404, detail="Node not found")
#
#     prompt = f"You are a social network node named {node.name}. Generate a short message."
#     message = await generate_message(prompt, model="llama3.1")
#     node.last_message = message
#     return {"message": message}


# @router.post("/nodes/{node_id}/get_embedding")
# async def get_node_embedding(node_id: int):
#     node = next((n for n in nodes if n.id == node_id), None)
#     if not node:
#         raise HTTPException(status_code=404, detail="Node not found")
#
#     if not node.last_message:
#         raise HTTPException(status_code=400, detail="Node has no message to embed")
#
#     embedding = await get_embedding(node.last_message, model="all-minilm")
#     return {"embedding": embedding}


# curl -X POST "http://localhost:8000/nodes/1/connect" -H "Content-Type: application/json" -d '{"target_node_id": "2"}'
# @router.post("/nodes/{node_id}/connect")
# async def connect_nodes(node_id: int, connection: NodeConnection):
#     source_node = next((n for n in nodes if n.id == node_id), None)
#     target_node = next((n for n in nodes if n.id == connection.target_node_id), None)
#
#     if not source_node or not target_node:
#         raise HTTPException(status_code=404, detail="One or both nodes not found")
#
#     if connection.target_node_id not in source_node.connections:
#         source_node.connections.append(connection.target_node_id)
#     if node_id not in target_node.connections:
#         target_node.connections.append(node_id)
#
#     return {"message": "Nodes connected successfully"}

# 创建连接
@router.post("/nodes/{node_id}/connect")
def connect_nodes(node_id: int, target_node_id: ConnectionCreate, db: Session = Depends(get_db)):
    return create_connection(db, node_id, target_node_id.target_node_id)


# curl -X POST "http://localhost:8000/nodes/1/interact"
# @router.post("/nodes/{node_id}/interact")
# async def node_interaction(node_id: int):
#     node = next((n for n in nodes if n.id == node_id), None)
#     if not node:
#         raise HTTPException(status_code=404, detail="Node not found")
#
#     connected_nodes = [n for n in nodes if n.id in node.connections]
#     context = "\n".join([f"{n.name}: {n.last_message}" for n in connected_nodes if n.last_message])
#
#     prompt = f"""You are a social network node named {node.name}.
#     Your connections have recently said:
#     {context}
#     Based on this, generate a short message as a response."""
#
#     message = await generate_message(prompt, model="llama3.1")
#     node.last_message = message
#     return {"message": message}

async def generate_memory_based_message(sender_node, receiver_node, db: Session):
    # Construct a prompt that includes the sender's memory and the context of the conversation
    prompt = f"""
    You are node {sender_node.name} with the following memory:
    {sender_node.memory}

    You are sending a message to node {receiver_node.name}.
    Based on your memory and personality, generate a message to send.
    """

    # Generate the message content
    message_content = await generate_message(prompt, model="llama3.1")

    # Update the sender's memory with this interaction
    new_memory = f"{sender_node.memory}\nSent message to {receiver_node.name}: {message_content}"
    update_node_memory(db, sender_node.id, new_memory)

    return message_content


@router.post("/messages/", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    sender_node = get_node(db, message.sender_id)
    receiver_node = get_node(db, message.receiver_id)

    if not sender_node or not receiver_node:
        raise HTTPException(status_code=404, detail="Sender or receiver node not found")

    # Generate message content using memory-based function
    generated_content = await generate_memory_based_message(sender_node, receiver_node, db)

    # Create message with generated content
    message.content = generated_content
    return create_message(db, message)


@router.get("/nodes/{node_id}/messages/", response_model=List[MessageResponse])
def get_node_messages(node_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = get_messages_for_node(db, node_id, skip=skip, limit=limit)
    return messages


async def conduct_dialogue(node1_id: int, node2_id: int, num_turns: int, db: Session = Depends(get_db)):
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
        sent_message = await send_message(message, db)

        dialogue_history.append({
            "turn": turn + 1,
            "sender": sender.name,
            "receiver": receiver.name,
            "content": sent_message.content
        })

        print(f"Turn {turn + 1}: {sender.name} to {receiver.name}: {sent_message.content}")

    return dialogue_history


@router.post("/start-dialogue/")
async def start_dialogue(node1_id: int, node2_id: int, num_turns: int = 5, db: Session = Depends(get_db)):
    try:
        dialogue_history = await conduct_dialogue(node1_id, node2_id, num_turns, db)
        return {"message": "Dialogue completed", "history": dialogue_history}
    except Exception as e:
        logger.error(f"Error during dialogue: {str(e)}")
        return {"error": "An error occurred during the dialogue", "details": str(e)}