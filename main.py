# Third-party imports
from fastapi import FastAPI, Form, Depends, HTTPException, status
from decouple import config
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import psycopg2

# Internal imports
from db.models import Conversation
from db.db import get_db
from chat.utils import send_message, logger
from ai.gemini import get_response


app = FastAPI()

whatsapp_number = config("TO_NUMBER")


@app.post("/message")
async def reply(Body: str = Form(), db: Session = Depends(get_db)):
    rollback = False

    try:
        chat_response = get_response(Body)

        if "SQLQuery" in chat_response:
            raise Exception("Error generaring the response.")

        # Store the conversation in the database
        conversation = Conversation(
            sender=whatsapp_number,
            message=Body,
            response=chat_response
        )
        db.add(conversation)
        db.commit()
        logger.info(f"Conversation #{conversation.id} stored in database")
        send_message(whatsapp_number, chat_response)

    except psycopg2.errors.SyntaxError as e:
        print(f"psycopg2 SyntaxError: {e}")
        rollback = True

    except SQLAlchemyError as e:
        print(f"SQLAlchemyError: {e}")
        send_error_message(e)
        rollback = True

    except Exception as e:
        print(f"Caught exception {e}")
        send_error_message(e)
        rollback = True

    if rollback:
        db.rollback()

    return ""


def send_error_message(e):
    logger.error(f"Error storing conversation in database: {e}")
    send_message(
        whatsapp_number,
        "I'm sorry, an error has occurred. Please send the message again or try sending another message."
    )
    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Error generaring the response")
