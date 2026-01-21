import os
from openai import OpenAI, AsyncOpenAI
from typing import List

openai_api_key = os.getenv("OPENAI_API_KEY")

# Sync client
client = OpenAI(api_key=openai_api_key)

# Async client
async_client = AsyncOpenAI(api_key=openai_api_key)


async def generate_embedding(
    text: str, model: str = "text-embedding-3-small"
) -> List[float]:
    """Generate embedding for text"""
    try:
        response = await async_client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        raise


async def generate_embedding_batch(
    texts: List[str], model: str = "text-embedding-3-small"
) -> List[List[float]]:
    """Generate embeddings for batch of texts"""
    try:
        response = await async_client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"Error generating batch embeddings: {e}")
        raise


async def chat_completion(
    messages: List[dict], model: str = "gpt-4", temperature: float = 0.7
) -> str:
    """Generate chat completion"""
    try:
        response = await async_client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating chat completion: {e}")
        raise
