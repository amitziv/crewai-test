import re
from crewai.tools import tool

@tool
def send_message(message: str, to_email: str):
    """Send a message to a specified email address.
    
    Args:
        message (str): The message content to send
        to_email (str): The email address to send the message to
        
    Returns:
        dict: Status of the message sending operation
    """
    # check email regex
    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
        return {"status": "error, invalid email"}

    print(f"Sending message to {to_email}: {message}")
    
    return {"status": f"success, message sent to {to_email}"}
