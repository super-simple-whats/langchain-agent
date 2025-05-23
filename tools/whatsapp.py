from langchain_core.tools import tool
from typing import Annotated
import os

@tool
def SendWhatsapp(
    recipient: Annotated[str, "The number of the WhatsApp contact to send the message. Should contain the country code, area code and number."],
    message: Annotated[str, "The message in plain text."],
) -> int:
    """Send a message to a informed WhatsApp contact. Use this when you want to send a message to a WhatsApp contact. If a required field was not provided, ask for it."""
    
    recipient = recipient.replace('"', "").replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")

    # Python equivalent of the PHP WhatsApp API call
    import requests

    # These would need to be properly defined elsewhere or passed as parameters
    endpoint_url = "https://app.supersimplewhats.com/v1"
    device_name = os.environ.get("DEVICE_NAME")
    api_key = os.environ.get("SSW_API_KEY")
    
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    
    try:
        response = requests.post(
            f"{endpoint_url}/messages/send/"+device_name+"/"+recipient,
            headers=headers,
            data=message
        )
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()  # Assuming the API returns JSON
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        raise
    