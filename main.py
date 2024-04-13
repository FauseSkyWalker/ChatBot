# Third-party imports
import openai
from fastapi import FastAPI, Form, Depends
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

# Internal imports
from db.models import Conversation
from db.db import get_db
from chat.utils import send_message, logger
from ai.gemini import get_response


app = FastAPI()
# Set up the OpenAI API client
openai.api_key = config("GOOGLE_API_KEY")
whatsapp_number = config("TO_NUMBER")


@app.get('/ping')
async def ping():
    return {"message": "pong"}


@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    chat_response = get_response(Body)

    # Store the conversation in the database
    try:
        conversation = Conversation(
            sender=whatsapp_number,
            message=Body,
            response=chat_response
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error storing conversation in database: {e}")

    # TO-DO: Pending to surround the next function in a try-catch block.
    send_message(whatsapp_number, chat_response)
    return ""
