"""
QA Endpoints - Core AI question answering

POST /qa/ask       → Single response
POST /qa/stream    → SSE streaming response
GET  /qa/history   → Conversation history
"""

import json
import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.qa import QARequest, QAResponse
from app.services.auth import get_current_user
from app.core.langgraph.graph import qa_graph

router = APIRouter()
logger = structlog.get_logger()


@router.post("/ask", response_model=QAResponse)
async def ask(request: QARequest, user=Depends(get_current_user)):
    """
    Single-shot QA: returns complete answer after full processing.
    """
    logger.info("QA request", user_id=user.id, query=request.query[:100])

    result = await qa_graph.ainvoke({
        "query": request.query,
        "user_id": user.id,
        "conversation_id": request.conversation_id,
    })

    return QAResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        chart=result.get("chart"),
        confidence=result.get("confidence", 0.0),
        trace_id=result.get("trace_id", ""),
    )


@router.post("/stream")
async def stream(request: QARequest, user=Depends(get_current_user)):
    """
    SSE streaming QA: streams processing steps and answer chunks in real-time.
    """
    logger.info("QA stream request", user_id=user.id, query=request.query[:100])

    async def generate():
        async for event in qa_graph.astream({
            "query": request.query,
            "user_id": user.id,
            "conversation_id": request.conversation_id,
        }):
            # Each event is a node completion in the LangGraph
            node_name = list(event.keys())[0]
            node_output = event[node_name]

            yield f"data: {json.dumps({'node': node_name, 'data': node_output}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/history")
async def get_history(conversation_id: str = None, user=Depends(get_current_user)):
    """
    Get conversation history for the current user.
    """
    from app.services.conversation import get_conversation_history
    history = await get_conversation_history(user.id, conversation_id)
    return {"conversations": history}
