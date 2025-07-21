# # In consumer.py
# from db import Session, Result
# from parser import extract_text_from_pdf
# from extractor import extract_fields, parse_response
# import logging
# logger = logging.getLogger(__name__)

# def process_pdf(file_bytes, filename):
#     session = Session()
#     try:
#         text = extract_text_from_pdf(file_bytes)
#         gpt_output = extract_fields(text)
#         parsed_result, error = parse_response(gpt_output)
#         if not parsed_result:
#             logger.error(f"GPT output parsing failed: {error}")
#             raise ValueError(f"Invalid GPT output: {error}")

#         # Save to Result table (same as dashboard)
#         result = Result(
#             payee=parsed_result.get("payee", ""),  # Default empty string
#             amount=parsed_result.get("amount", 0.0),
#             amount_type=parsed_result.get("amount_type"),
#             iban=parsed_result.get("amount_type"),
#             # Add other fields as needed
#         )
#         session.add(result)
#         session.commit()
#         logger.info(f"Saved results for {filename} to DB")

#     except Exception as e:
#         session.rollback()
#         logger.error(f"Failed to process {filename}: {e}")
#     finally:
#         session.close()

import pika
import json
import base64
import logging
import time
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker
from db import Session, Result
from parser import extract_text_from_pdf
from extractor import extract_fields, parse_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_pdf(file_bytes, filename):
    """Process PDF bytes directly (no file object needed)"""
    session = Session()
    try:
        # Process raw bytes directly
        text = extract_text_from_pdf(file_bytes)  # Ensure this accepts bytes
        logger.debug(f"Extracted text from {filename} ({len(text)} chars)")
        
        gpt_output = extract_fields(text)
        parsed_result, error = parse_response(gpt_output)
        
        if not parsed_result:
            raise ValueError(f"GPT parsing failed: {error}")

        result = Result(
            payee=parsed_result.get("payee", ""),
            amount=parsed_result.get("amount", 0.0),
            amount_type=parsed_result.get("amount_type", ""),
            iban=parsed_result.get("iban", ""),
        )
        session.add(result)
        session.commit()
        logger.info(f"✅ Successfully processed {filename}")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to process {filename}: {e}")
        raise
    finally:
        session.close()

def start_consumer():
    """Main consumer loop with reconnection logic"""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            channel = connection.channel()
            
            channel.queue_declare(queue='documents', durable=True)
            
            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body)
                    # Get raw bytes directly (no file object conversion)
                    file_bytes = base64.b64decode(payload['file_bytes'])
                    filename = payload.get('filename', 'unknown.pdf')
                    
                    logger.info(f"📨 Processing {filename}")
                    process_pdf(file_bytes, filename)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    logger.error(f"🚨 Processing failed: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(
                queue='documents',
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("🛎️ Consumer ready - waiting for messages...")
            channel.start_consuming()

        except AMQPConnectionError:
            logger.error("RabbitMQ connection failed - retrying in 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("👋 Shutting down gracefully...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e} - restarting in 10s")
            time.sleep(10)

if __name__ == "__main__":
    start_consumer()