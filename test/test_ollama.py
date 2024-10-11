import asyncio
import httpx

OLLAMA_URL = "http://localhost:11434/api/generate"


async def test_ollama():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": "llama3.1",
                    "prompt": "Say this is a test",
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            print("Success!")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
            if isinstance(e, httpx.HTTPStatusError):
                print(f"Response content: {e.response.text}")

asyncio.run(test_ollama())