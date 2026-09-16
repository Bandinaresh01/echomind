import base64
from email.message import EmailMessage
from typing import Optional
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service(creds_dict: dict):
    if not creds_dict:
        raise ValueError("Google Credentials missing. Cannot use Gmail.")
    creds = Credentials(
        token=creds_dict.get("access_token"),
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict.get("token_uri"),
        client_id=creds_dict.get("client_id"),
        client_secret=creds_dict.get("client_secret"),
        scopes=creds_dict.get("scopes")
    )
    return build('gmail', 'v1', credentials=creds)

def create_read_emails_tool(creds_dict: dict):
    @tool
    def read_recent_emails() -> str:
        """Reads the last 5 recent emails from the user's Gmail inbox. Useful to check mail or summarize recent activity."""
        try:
            service = get_gmail_service(creds_dict)
            results = service.users().messages().list(userId='me', maxResults=5).execute()
            messages = results.get('messages', [])
            
            if not messages:
                return "Your inbox is empty."
                
            email_texts = []
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject', 'Date']).execute()
                headers = msg_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                snippet = msg_data.get('snippet', '')
                email_texts.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n")
                
            return "\n---\n".join(email_texts)
        except Exception as e:
            return f"Failed to read emails: {str(e)}"
            
    return read_recent_emails

def create_send_email_tool(creds_dict: dict):
    @tool
    def send_email(to: str, subject: str, body: str) -> str:
        """Sends an email using the user's Gmail account. Provide exactly three arguments: 'to' (email address), 'subject' (str), and 'body' (str)."""
        try:
            service = get_gmail_service(creds_dict)
            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['Subject'] = subject
            
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            send_message = service.users().messages().send(userId="me", body=create_message).execute()
            return f"Email sent successfully to {to}. Message ID: {send_message['id']}"
        except Exception as e:
            return f"Failed to send email: {str(e)}"
            
    return send_email
