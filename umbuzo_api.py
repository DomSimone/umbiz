import uvicorn
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import os
import sys
import io
import logging
import json
import asyncio

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("umbuzo_backend")

# --- Voice Assistant Integration ---
import speech_recognition as sr
from gtts import gTTS
# -----------------------------------

# --- Web Search Integration ---
try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search_tool = DuckDuckGoSearchRun()
    logger.info("DuckDuckGo Search Tool initialized.")
except ImportError:
    logger.warning("DuckDuckGo Search not found. Web search will be disabled.")
    search_tool = None
# ------------------------------

# --- FIX FOR CUDA_PATH ERROR ---
if "CUDA_PATH" in os.environ:
    cuda_path = os.environ["CUDA_PATH"]
    if not os.path.exists(cuda_path):
        print(f"WARNING: CUDA_PATH is set to '{cuda_path}' but does not exist.")
        print("Unsetting CUDA_PATH for this session to prevent crash.")
        del os.environ["CUDA_PATH"]
    else:
        cuda_bin = os.path.join(cuda_path, "bin")
        if not os.path.exists(cuda_bin):
            print(f"WARNING: CUDA_PATH/bin not found at '{cuda_bin}'.")
            print("Unsetting CUDA_PATH for this session to prevent crash.")
            del os.environ["CUDA_PATH"]
# -------------------------------

# Attempt to import llama_cpp
try:
    from llama_cpp import Llama
except ImportError:
    print("Error: llama-cpp-python is not installed. Please install it with:")
    print("pip install llama-cpp-python")
    sys.exit(1)
except Exception as e:
    print(f"Critical Error importing llama_cpp: {e}")
    sys.exit(1)

app = FastAPI(title="Umbuzo AI Backend", description="Backend for Umbuzo GGUF Model")

# --- HUGGING FACE MODEL CONFIGURATION ---
MODEL_REPO = "DomSimone/Umbuzo"
# Switched to a 4-bit quantized model to reduce memory usage.
MODEL_FILENAME = "umbuzo-gemma-2b-v3data.q4_K_M.gguf"
# ----------------------------------------

llm = None

def load_model():
    global llm
    try:
        logger.info(f"Attempting to download model '{MODEL_FILENAME}' from Hugging Face repo '{MODEL_REPO}'...")
        
        # Check for HF_TOKEN in environment variables
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            logger.info("HF_TOKEN found in environment variables.")
        
        llm = Llama.from_pretrained(
            repo_id=MODEL_REPO,
            filename=MODEL_FILENAME,
            token=hf_token,
            n_ctx=2048,  # Reduced context size to save memory
            n_threads=4,
            verbose=True
        )
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.critical(f"FATAL: Failed to load model: {e}")
        print("Please ensure an internet connection is active and the model repository is correct.")
        print("If the model is gated or private, ensure you have set the HF_TOKEN environment variable.")

# Request Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[ChatMessage]] = []
    topic: Optional[str] = "default"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    use_search: Optional[bool] = False # New flag for web search

class ChatResponse(BaseModel):
    query: str
    response: str
    topic: str
    tokens_used: int
    generation_time: float
    timestamp: float
    model: str = "Umbuzo-GGUF"

# System Prompts based on Topics
TOPIC_PROMPTS = {
    "Political And Civic Engagement": "You are an expert in African political and civic engagement. Focus on voting patterns, cultural dynamics, and societal impact.",
    "Economic And Labor Trends": "You are an expert in African economics. Focus on income, poverty, employment, and agriculture.",
    "Urban and community dynamics": "You are an expert in African urban planning and community dynamics. Focus on urbanization, crime statistics, and community services.",
    "Demographic Trends": "You are an expert in African demographics. Focus on migration, age structures, diversity, family structures, housing, education, and health.",
    "default": "You are Umbuzo, an AI assistant specialized in African history, current affairs, and academics. Provide helpful, accurate, and context-aware responses."
}

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health_check():
    status = "healthy" if llm else "loading_or_error"
    return {"status": status, "model": f"{MODEL_REPO}/{MODEL_FILENAME}", "timestamp": time.time()}

def build_prompt(query: str, topic: str, history: List[dict], search_context: str = "") -> str:
    system_prompt = TOPIC_PROMPTS.get(topic, TOPIC_PROMPTS["default"])
    
    if search_context:
        system_prompt += f"\n\nContext from Web Search:\n{search_context}\n\nUse this context to answer the user's question if relevant."

    # --- GEMMA PROMPT FORMATTING ---
    prompt = f"<start_of_turn>user\nSystem: {system_prompt}\n\n"
    
    for msg in history[-5:]:
        role = "user" if msg.get('role') == "user" else "model"
        prompt += f"<start_of_turn>{role}\n{msg.get('content')}<end_of_turn>\n"
    
    prompt += f"<start_of_turn>user\n{query}<end_of_turn>\n<start_of_turn>model\n"
    return prompt

# --- WebSocket Endpoint for Streaming ---
@app.websocket("/chat/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive JSON payload
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            query = request_data.get("query")
            topic = request_data.get("topic", "default")
            history = request_data.get("conversation_history", [])
            use_search = request_data.get("use_search", False)
            
            if not llm:
                await websocket.send_text(json.dumps({"error": "Model not loaded"}))
                continue

            # Perform Web Search if requested
            search_context = ""
            if use_search and search_tool:
                try:
                    await websocket.send_text(json.dumps({"status": "Searching the web..."}))
                    logger.info(f"Searching web for: {query}")
                    # Run search in a thread to avoid blocking the event loop
                    search_context = await asyncio.to_thread(search_tool.run, query)
                    logger.info(f"Search results found: {len(search_context)} chars")
                except Exception as e:
                    logger.error(f"Search failed: {e}")
                    await websocket.send_text(json.dumps({"status": "Search failed, using internal knowledge."}))

            prompt = build_prompt(query, topic, history, search_context)
            logger.info(f"Streaming prompt: {prompt[:50]}...")

            # Stream tokens
            stream = llm(
                prompt,
                max_tokens=1024,
                stop=["<end_of_turn>"],
                temperature=0.7,
                stream=True # Enable streaming
            )

            for output in stream:
                token = output['choices'][0]['text']
                # Send token immediately
                await websocket.send_text(json.dumps({
                    "token": token,
                    "done": False
                }))
                # Small yield to ensure event loop processing
                await asyncio.sleep(0)

            # Signal completion
            await websocket.send_text(json.dumps({"done": True}))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except:
            pass

# --- Standard HTTP Endpoint (Legacy/Fallback) ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not llm:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    
    start_time = time.time()
    
    search_context = ""
    if request.use_search and search_tool:
        try:
            search_context = search_tool.run(request.query)
        except Exception as e:
            logger.error(f"Search failed: {e}")

    prompt = build_prompt(request.query, request.topic, [m.dict() for m in request.conversation_history], search_context)
    
    output = llm(
        prompt,
        max_tokens=1024,
        stop=["<end_of_turn>"],
        temperature=0.7,
        echo=False
    )
    response_text = output['choices'][0]['text'].strip()
    
    return ChatResponse(
        query=request.query,
        response=response_text,
        topic=request.topic,
        tokens_used=0, 
        generation_time=time.time() - start_time,
        timestamp=time.time()
    )

# --- Voice Assistant Endpoint ---
@app.post("/chat/voice")
async def voice_chat_endpoint(audio_file: UploadFile = File(...)):
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file.file) as source:
            audio_data = recognizer.record(source)
        user_text = recognizer.recognize_google(audio_data)
        logger.info(f"Transcribed voice: '{user_text}'")
    except Exception as e:
        logger.error(f"Speech recognition error: {e}")
        raise HTTPException(status_code=400, detail="Could not understand audio.")

    # For voice, we default search to False for speed, or could add a keyword trigger
    prompt = build_prompt(user_text, "default", [])
    output = llm(prompt, max_tokens=1024, stop=["<end_of_turn>"], temperature=0.7)
    response_text = output['choices'][0]['text'].strip()

    try:
        tts = gTTS(text=response_text, lang='en')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio response.")

    return StreamingResponse(audio_bytes, media_type="audio/mpeg")

# --- Serve Frontend ---
@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

app.mount("/", StaticFiles(directory="frontend"), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
