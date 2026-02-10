# creating app.py backend code.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.core.ai_agent import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

# initialize logger
logger = get_logger(__name__)


# initialize app
app = FastAPI(title = "MULti AI agent")

class RequestState(BaseModel):
    model_name = str
    system_prompt = str
    messages = List[str]
    allow_search = bool

@app.post("/chat")
def chat_endpoint(request:RequestState):
    logger.info(f" received request for model: {request.model_name}")

    if request.model_name not in settings.ALLOWED_MODEL_NAMES:
        logger.warning("Invalid model name")
        raise HTTPException(status_code=400, detail="Invalid model name")
    
    try:
        response = get_response_from_ai_agents(
            request.model_name,
            request.messages,
            request.allow_search,
            request.system_prompt
        )

        logger.info(f"successfully got response from AI agent {request.model_name}")
        return {"response" : response}

    except Exception as e:
        logger.error("some error occured during response generation")
        raise HTTPException(
            status_code=500, details=str(CustomException("Failed to get AI response", error_detail=e))
        )







import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
logger = get_logger(__name__)


st.set_page_config(page_title="mutlit_ai_agent", layout="centered")
st.title("multi AI agent using groq and tavily")
system_prompt = st.text_area("define your ai agent: ", height=70)
selected_model = st.selectbox("select your ai model: " , settings.ALLOWED_MODEL_NAMES)
allow_web_search = st.checkbox("allow web search")
user_query = st.text_area("enter your query: ", height= 150)

API_URL = "http://127.0.0.1:9999/chat"

if st.button("ask agent") and user_query.strip():
    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt,
        "messages": [user_query],
        "allow_search": allow_web_search
    }

    try:
        logger.info("sending request to backend")
        response = requests.post(API_URL, json=payload)
        if response.status_code ==200:
            agent_response = response.json().get("response", "")
            logger.info("successfully received response from backend")

            st.subheader("agent response")
            st.markdown(agent_response.replace("\n","<br>"), unsafe_allow_html=True)
        
        else:
            logger.error("backend error")
            st.error("error with backend")
    
    except Exception as e:
        logger.error("error occured while sending request to backend")
        st.error(str(CustomException("Failed to communicate to backend")))




# main.py
import subprocess
import threading
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

def run_bakcend():
    try:
        logger.info("starting backend serivce...")
        subprocess.run(["uvicorn" , "app.backend.api:app" , " --host", "127.0.0.1", "--port" , "9999"], check=True)
    except CustomException as e:
        logger.error("promblem with backend service")
        raise CustomException("Failed to start backend" , e)





def run_frontend():
    try:
        logger.info(" running frontend service ...")
        subprocess.run(["streamlit", "run" , "app/frontend/ui.py"], check=True)
    except Exception as e:
        logger.error("something went wrong with frontend ...")
        raise CustomException("failed to start frontend", e)

if __name__ =="__main__":
    try:
        threading.Thread(target=run_bakcend).start()
        time.sleep(2)
        run_frontend()
    except CustomException as e:
        logger.exception(f"custom exeption occured: {str(e)}")


    
    

