
# import streamlit as st
# from parser import extract_text_from_pdf
# from extractor import extract_fields, parse_response
# from db import save_to_db
# import logging
# from dotenv import load_dotenv
# import pika
# import json

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load env vars for local development
# load_dotenv()
# # Streamlit UI setup
# st.set_page_config(page_title="Document Extractor", layout="centered")
# st.title("📄 Document Extractor (GPT-4o)")

# # File uploader
# uploaded_file = st.file_uploader("Upload an insurance document (PDF)", type="pdf")
# st.success("✅ File sent for processing. Refresh the dashboard later.")

# if uploaded_file:
#     st.info("Extracting text from PDF...")
#     try:
#         text = extract_text_from_pdf(uploaded_file)
#         st.success("Text extracted. Sending to GPT-4o...")
#     except Exception as e:
#         logger.error(f"PDF parsing error: {e}")
#         st.error("Failed to extract text from PDF.")
#         st.stop()

#     # Extract structured fields from GPT
#     try:
#         gpt_output = extract_fields(text)
#         st.code(gpt_output, language='json')  # raw view for debugging
#     except Exception as e:
#         logger.error(f"GPT API error: {e}")
#         st.error("Failed to extract information using GPT-4o.")
#         st.stop()

#     # Parse and validate output
#     parsed_result, error = parse_response(gpt_output)

#     if parsed_result:
#         st.subheader("🧾 Extracted Fields")
#         st.json(parsed_result)

#         try:
#             save_to_db(parsed_result)
#             st.success("✅ Result saved to database.")
#             logger.info("Extraction saved successfully.")
#         except Exception as e:
#             logger.error(f"DB save error: {e}")
#             st.warning("Extraction succeeded, but saving to database failed.")
#     else:
#         st.error("❌ GPT output could not be validated.")
#         st.text(error)



### with rabbitmq

import pika
import json
import base64
import logging
import streamlit as st
from pika.exceptions import AMQPConnectionError  # Add this import

def send_to_queue(uploaded_file):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', heartbeat=600)
        )
        channel = connection.channel()
        
        # Match the queue declaration with consumer
        channel.queue_declare(queue='documents', durable=True)
        
        file_bytes = uploaded_file.read()
        payload = {
            'file_bytes': base64.b64encode(file_bytes).decode('utf-8'),
            'filename': uploaded_file.name
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='documents',
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        connection.close()
        return True
    except AMQPConnectionError:
        st.error("❌ Cannot connect to RabbitMQ. Is the server running?")
        return False
    except Exception as e:
        st.error(f"❌ Queue error: {str(e)}")
        return False

# ✅ Streamlit UI section
st.title("📄 Document Uploader")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])

if uploaded_file is not None and st.button("Process"):
    if send_to_queue(uploaded_file):
        st.success("✅ File sent for processing!")
    else:
        st.error("❌ Failed to send file to queue")
