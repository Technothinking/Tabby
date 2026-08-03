import asyncio
import os
import sys

# Append backend path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.agent.state import AgentState
from app.agent.memory.condenser import TraceCondenser
from app.agent.memory.embeddings import Embedder
from app.agent.memory.writer import MemoryWriter
from app.agent.memory.retriever import MemoryRetriever
from app.db.session import async_session
from app.db.models import Run
import uuid

async def test_memory():
    run_id = uuid.uuid4()
    
    async with async_session() as session:
        session.add(Run(id=run_id, goal="Search for Macbook Pro", status="completed"))
        await session.commit()
        
    mock_state = {
        "run_id": str(run_id),
        "goal": "Search for latest Macbook Pro models",
        "status": "completed",
        "action_history": [
            {
                "proposed_action": type('MockAction', (), {"type": "navigate", "target_id": None, "rationale": "Go to google"}),
                "result_status": True
            },
            {
                "proposed_action": type('MockAction', (), {"type": "type", "target_id": "search_el", "rationale": "Type macbook pro"}),
                "result_status": True
            }
        ]
    }
    
    print("1. Condensing trace...")
    summary = await TraceCondenser.condense(mock_state)
    print("Summary Generated:", summary.model_dump_json(indent=2))
    
    print("2. Embedding trace...")
    embedding = await Embedder.embed_trace(summary.model_dump())
    print("Embedded Vector Length:", len(embedding))
    
    print("3. Persisting to database...")
    await MemoryWriter.persist_trace(mock_state["run_id"], summary.model_dump(), embedding)
    print("Persisted successfully.")
    
    print("4. Retrieving based on related goal...")
    hints = await MemoryRetriever.retrieve_hints("Search for Apple laptops", domain_hint="unknown", top_k=2)
    print("Hints Retrieved:")
    for h in hints:
        print(f"- Domain: {h['domain']}, Outcome: {h['outcome']}")
    

if __name__ == "__main__":
    asyncio.run(test_memory())
