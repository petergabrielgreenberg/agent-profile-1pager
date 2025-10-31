query = f'to:{TARGET_EMAIL} is:unread'
results = service.users().messages().list(userId='me', q=query).execute()

messages = results.get('messages', [])
count = len(messages)

print(f"Unread emails to {TARGET_EMAIL}: {count}")

if messages:
    print("\nMessages found:")
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject']
        ).execute()
        
        headers = msg_data['payload']['headers']
        from_h = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        subj = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        
        print(f"  - From: {from_h}")
        print(f"    Subject: {subj}")