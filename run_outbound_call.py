import os
import telnyx
from dotenv import load_dotenv

load_dotenv()

telnyx.api_key = os.environ.get('TELNYX_API_KEY')
connection_id = os.environ.get('TELNYX_CONNECTION_ID')
my_us_number = os.environ.get('MY_US_NUMBER')
customer_number = os.environ.get('CUSTOMER_NUMBER_TO_TEST')

print("Initiating call...")

try:
    new_call = telnyx.Call.create(
        to=customer_number,
        from_=my_us_number,
        connection_id=connection_id,
    )
    print(f"Call initiated with Control ID: {new_call.call_control_id}")
except Exception as e:
    print(f"Error making call: {e}")