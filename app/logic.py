import smtplib
def get_response_from_logic(customer_input_text):
    text = customer_input_text.lower()
    if "how much" in text or "price" in text:
        return "Our comprehensive luxury renovations are a significant investment. To give you an accurate idea, we would need to schedule a consultation. Are you available next week?"
    # ... more rules from Objection Handling Pack
    else:
        return "I see. Could you tell me more about the vision you have for your space?"

def check_for_handoff(customer_input_text):
    text = customer_input_text.lower()
    if "yes i am available" in text or "book the meeting" in text:
        return True
    return False


import smtplib

def trigger_handoff_email(call_details):
    # NOTE: You'll need to set email credentials as environment variables in Azure
    sender_email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver_email = "operations@metamorphic.ae"

    message = f"""Subject: New Qualified Lead - Handoff

    A new lead has been qualified by the Omar AI Agent.

    Details:
    - Caller Number: {call_details.get('customer_number')}
    - Outcome: Agreed to a consultation.

    Please follow up immediately.
    """
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        print("Handoff email sent successfully.")
    except Exception as e:
        print(f"Failed to send handoff email: {e}")