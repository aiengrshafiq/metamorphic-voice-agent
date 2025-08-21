## File: app/main.py (Definitive Version)

from fastapi import FastAPI, Request, Response
import telnyx
import os
import requests
import json
from dotenv import load_dotenv
import traceback

load_dotenv()
telnyx.api_key = os.environ.get('TELNYX_API_KEY')
ASSISTANT_ID = os.environ.get('ASSISTANT_ID')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL') 
app = FastAPI()

# --- Helper function to call the REST API directly ---
TELNYX_API_BASE = "https://api.telnyx.com/v2"

def start_ai_assistant_http(call_control_id: str, body: dict):
    url = f"{TELNYX_API_BASE}/calls/{call_control_id}/actions/ai_assistant_start"
    headers = {
        "Authorization": f"Bearer {telnyx.api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    print(f"Sending POST to {url} with body: {json.dumps(body, indent=2)}")
    r = requests.post(url, json=body, headers=headers, timeout=15)
    
    try:
        payload = r.json()
    except Exception:
        payload = {"raw_text": r.text}
    if r.status_code >= 400:
        raise RuntimeError(f"start_ai_assistant failed with status {r.status_code}: {payload}")
    return payload

def send_slack_notification(name, villa_details, mobile_number, client_type):
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not set. Skipping notification.")
        return
    
    message = {
        "text": f"🎉 New Qualified Lead ({client_type}): {name}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"🎉 New Qualified Lead ({client_type})"}},
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Customer Name:*\n{name}"},
                    {"type": "mrkdwn", "text": f"*Contact Number:*\n{mobile_number}"},
                    {"type": "mrkdwn", "text": f"*Villa Details:*\n{villa_details}"}
                ]
            },
            {"type": "divider"},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": "Handoff to Operations & QS Team for immediate follow-up."}]}
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message, timeout=10)
        response.raise_for_status()
        print("Successfully sent Slack notification.")
    except Exception as e:
        print(f"Error sending Slack notification: {e}")

@app.post("/telnyx/events")
async def handle_webhook(request: Request):
    try:
        event_json = await request.json()
        event = telnyx.Event.construct_from(event_json, telnyx.api_key)
        event_type = event.data.event_type
        payload = event.data.payload
        
        print(f"Received Event: {event_type}")

        if event_type == "call.answered":
            call_control_id = payload.get('call_control_id')
            print(f"Processing Call ID: {call_control_id}")
            call = telnyx.Call.retrieve(call_control_id)
            
            call.suppression_start(direction="inbound")
            
            start_ai_assistant_http(
                call_control_id,
                {
                    "assistant": { "id": ASSISTANT_ID },
                    "voice": "AWS.Polly.Joanna-Neural",
                    "greeting": "Hello, this is Omar from Metamorphic Design.",
                    "interruption_settings": { "enable": True },
                    "transcription": {
                        "model": "distil-whisper/distil-large-v2",
                        # --- THE FIX: Language must be specified here for STT ---
                        "language": "en"
                    }
                }
            )

        elif event_type == "call.ai_assistant.tool_calls":
            tool_calls = payload.get("tool_calls", [])
            for tool_call in tool_calls:
                function_name = tool_call.get("function", {}).get("name")
                if function_name == "capture_lead_details":
                    arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                    print("--- HANDOFF TRIGGERED: LEAD DETAILS CAPTURED ---")
                    send_slack_notification(arguments.get('name'), arguments.get('villa_details'), arguments.get('mobile_number'), arguments.get('client_type', 'New Client'))

        elif event_type == "call.ai_assistant.ended":
            call_control_id = payload.get('call_control_id')
            print(f"AI Assistant session has ended for call: {call_control_id}.")
            try:
                call = telnyx.Call.retrieve(call_control_id)
                call.hangup()
            except Exception as e:
                print(f"Call already ended, no action needed: {e}")

    except Exception as e:
        print(f"--- AN EXCEPTION OCCURRED IN MAIN WEBHOOK ---")
        print(f"Error: {repr(e)}")
        traceback.print_exc()
        print(f"--- END OF EXCEPTION ---")
    
    return Response(status_code=200)

@app.post("/telnyx/tool_handler")
async def handle_tool_webhook(request: Request):
    """Handles the data sent from our 'capture_lead_details' webhook tool."""
    # This endpoint remains as a best practice for webhook-type tools.
    # The current 'capture_lead_details' tool uses the tool_calls event instead.
    return Response(status_code=200)