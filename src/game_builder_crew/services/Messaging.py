import re
from crewai.tools import tool

@tool
def send_message(message: str, to_email: str):
    # check email regex
    if not re.match(r"[^@]+@[^@]+\.[^@]+", to_email):
        return {"status": "error, invalid email"}

    print(f"Sending message to {to_email}: {message}")
    
    return {"status": f"success, message sent to {to_email}"}
