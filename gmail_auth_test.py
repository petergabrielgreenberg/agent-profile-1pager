# gmail_auth.py (I'll create this for you)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Specific email address to monitor
TARGET_EMAIL = 'gabrielgreenberg1+profile1pager@gmail.com'

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

service = build('gmail', 'v1', credentials=creds)
        
# Get user profile
profile = service.users().getProfile(userId='me').execute()
email_address = profile.get('emailAddress')
total_messages = profile.get('messagesTotal')

print(f"✅ Successfully connected to Gmail!")
print(f"📧 Email: {email_address}")
print(f"📬 Total messages: {total_messages}")

print(profile)

print(f"\n🔍 Testing filter for: {TARGET_EMAIL}")
query = f'to:{TARGET_EMAIL} is:unread'
results = service.users().messages().list(
    userId='me',
    q=query,
    maxResults=1
).execute()
print(results)
print(len(results['messages']))
print(results.get('resultSizeEstimate', 0))

if 'messages' in results and len(results['messages']) > 0:
    print("✅ There are messages 📧📧")
else:
    print("No messages")


# def authenticate_gmail():
#     """Authenticate and return Gmail service"""
#     creds = None
    
#     # Token.json stores access and refresh tokens
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
#     # If no valid credentials, let user log in
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'google_credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         # Save credentials for next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
    
#     return creds

# if __name__ == '__main__':
#     print("Authenticating with Gmail...")
#     creds = authenticate_gmail()
#     print("✅ Authentication successful!")
#     print("token.json has been created for future use.")