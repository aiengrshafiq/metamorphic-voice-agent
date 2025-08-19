from fastapi import FastAPI, Request, Response
import telnyx
import os

# It's good practice to also configure the SDK here
telnyx.api_key = os.environ.get('TELNYX_API_KEY')

app = FastAPI()

@app.post("/telnyx/events")
async def handle_webhook(request: Request):
    event_json = await request.json()
    event = telnyx.Event.construct_from(event_json, telnyx.api_key)

    print(f"Received Event: {event.data.event_type}")

    # Your logic will go here
    event_json = await request.json()
    event = telnyx.Event.construct_from(event_json, telnyx.api_key)

    event_type = event.data.event_type
    payload = event.data.payload

    print(f"Received Event: {event_type}")

    if event_type == "call.initiated":
        # Create a Call object to control the live call
        call = telnyx.Call(call_control_id=payload.get('call_control_id'))
        call.answer()

    elif event_type == "call.answered":
        call = telnyx.Call(call_control_id=payload.get('call_control_id'))

        # 1. SPEAK (TTS)
        greeting = "Hello, this is Omar calling from Metamorphic Design in Al Barsha."
        call.speak(payload=greeting, voice='en-US_AllisonV3Voice')

        # 2. LISTEN (STT)
        call.gather_using_speech(
            prompt="To confirm, are you the owner of the property?",
            valid_speech=["yes", "no", "maybe"] # Example grammar
        )

    elif event_type == "gather.ended":
        transcribed_text = payload.get("result")
        print(f"Customer said: {transcribed_text}")

        # Here you will call your business logic
        # For now, let's just say goodbye
        call = telnyx.Call(call_control_id=payload.get('call_control_id'))
        call.speak(payload="Thank you for your time. Goodbye.", voice='en-US_AllisonV3Voice')
        call.hangup()

    return Response(status_code=200)

   