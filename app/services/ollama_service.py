import httpx
import json
from typing import List, Union

OLLAMA_URL = "http://localhost:11434/api/generate"


async def generate_message(prompt: str, model: str = "llama3.1") -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0  # 增加超时时间到60秒
            )
            response.raise_for_status()
            return response.json()["response"]
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response content: {e.response.text}")
            return f"Error generating message: HTTP {e.response.status_code}"
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            return f"Error generating message: {str(e)}"
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {response.text}")
            return "Error generating message: Invalid JSON response"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"Error generating message: Unexpected error"


async def get_embedding(texts: Union[str, List[str]], model: str = "all-minilm") -> List[List[float]]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": texts if isinstance(texts, str) else "\n".join(texts),
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["embedding"] if "embedding" in result else []
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []