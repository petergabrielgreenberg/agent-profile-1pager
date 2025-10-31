#!/usr/bin/env python3
"""
Email Monitor - Checks for new research requests
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import sys
from datetime import datetime

# Target email address to monitor
TARGET_EMAIL = 'gabrielgreenberg1+profile1pager@gmail.com'

# Check interval (seconds)
CHECK_INTERVAL = 30

def get_gmail_service():
    """
    Create and return Gmail API service
    """
    if not os.path.exists('token.json'):
        print("❌ ERROR: token.json not found!")
        print("Please run 'python gmail_auth.py' first to authenticate.")
        sys.exit(1)
    
    try:
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Error creating Gmail service: {e}")
        sys.exit(1)

def check_for_new_emails(service):
    """
    Check for unread emails sent to target address
    Returns: List of message objects (if any found)
    """
    try:
        query = f'to:{TARGET_EMAIL} is:unread'
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1  # Process one at a time
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    
    except HttpError as error:
        print(f"❌ Gmail API error: {error}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error checking emails: {e}")
        return []

def parse_email(service, message_id):
    """
    Parse email to extract sender, subject (company name), and other details
    
    Returns: Dictionary with email data
    """
    try:
        # Get full message details
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = message['payload']['headers']
        
        # Get key fields
        from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
        
        # FUTURE UPDATE: include some
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Unknown Company')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
        
        # Extract body (if needed for additional context)
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            import base64
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        email_data = {
            'message_id': message_id,
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'company_name': subject.strip(),  # Use subject as company name
            'body': body.strip() if body else '',
            'date': date
        }
        
        return email_data
    
    except Exception as e:
        print(f"❌ Error parsing email {message_id}: {e}")
        return None

def mark_as_read(service, message_id):
    """
    Mark email as read (remove UNREAD label)
    """
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Error marking message as read: {e}")
        return False

def main():
    """
    Main monitoring loop
    """
    import os  # Add this import
    
    print("="*70)
    print("📧 Email Research Agent - Monitoring Mode")
    print("="*70)
    print(f"Target Email: {TARGET_EMAIL}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    # Get Gmail service
    service = get_gmail_service()
    
    # Monitoring loop
    loop_count = 0
    
    try:
        while True:
            loop_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"[{timestamp}] 🔍 Checking for new emails... (check #{loop_count})")
            
            # Check for new emails
            messages = check_for_new_emails(service)
            
            if messages:
                print(f"✅ Found {len(messages)} unread message(s)")
                
                # Process each message
                for msg in messages:
                    message_id = msg['id']
                    print(f"\n{'─'*70}")
                    print(f"📨 Processing message: {message_id}")
                    
                    # Parse email
                    email_data = parse_email(service, message_id)
                    
                    if email_data:
                        print(f"From: {email_data['from']}")
                        print(f"To: {email_data['to']}")
                        print(f"Subject: {email_data['subject']}")
                        print(f"Company Name: {email_data['company_name']}")
                        print(f"Date: {email_data['date']}")
                        if email_data['body']:
                            print(f"Body Preview: {email_data['body'][:100]}...")
                        
                        print(f"\n🤖 [PLACEHOLDER] Would process research for: {email_data['company_name']}")
                        print(f"📤 [PLACEHOLDER] Would send results to: {email_data['from']}")
                        
                        # Mark as read
                        if mark_as_read(service, message_id):
                            print(f"✓ Marked as read")
                        
                        print(f"{'─'*70}\n")
                    else:
                        print(f"❌ Failed to parse email")
            else:
                print("   No new messages")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print(f"Total checks performed: {loop_count}")
        print("="*70)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()