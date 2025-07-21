import pika, json
from extractor import extract_fields, parse_response
from db import save_to_db
from parser import extract_text_from_pdf
from io import BytesIO

# Connect to RabbitMQ (default local)
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()
# channel.queue_declare(queue='documents')

def callback(ch, method, properties, body):
    print("🟢 Received document")

    try:
        payload = json.loads(body)
        file_bytes = bytes(payload['file_bytes'])

        from io import BytesIO
        text = extract_text_from_pdf(BytesIO(file_bytes))

        gpt_output = extract_fields(text)
        print("🔍 Raw GPT output:")
        print(gpt_output)

        result, error = parse_response(gpt_output)
        print("✅ Parsed result:", result)
        if error:
            print("⚠️ Validation error:", error)

        if result and all(v is not None for v in result.values()):
            
            # Optional: log if any field is missing
            missing = [k for k, v in result.items() if v is None]
            if missing:
                print(f"⚠️ Missing fields: {missing}")
            
            print(f"📝 Saving to DB with data: {result!r}")
            save_to_db(result)
            print("✅ Saved to DB")
        else:
            print("❌ GPT output could not be validated. Skipping DB save.")

    except Exception as e:
        print("💥 Worker error:", e)


# channel.basic_consume(queue='documents', on_message_callback=callback, auto_ack=True)
# print("📡 Worker listening...")
# channel.start_consuming()
