import json

def lambda_handler(event, context):
    try:
        # Handle the body whether it's a string or dict
        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        # Get the search query from the body
        search_query = body.get('query', '').lower()
        
        # Extract conversations from the body
        conversations = body.get('conversations', [])
        
        # Split the search query into individual words
        search_words = search_query.split()
        
        # Search for conversations containing all the search words in translations
        matching_conversations = []
        
        for conversation in conversations:
            # Search through all translations in the conversation
            found_match = False
            
            for translation in conversation.get('translations', []):
                # Create a combined text from relevant fields to search
                searchable_text = ' '.join([
                    translation.get('translationText', '').lower(),
                    translation.get('translated', '').lower(),
                    translation.get('brandContext', '').lower(),
                    translation.get('reason', '').lower()
                ])
                
                # Check if all search words are in the text
                if all(word in searchable_text for word in search_words):
                    matching_conversations.append({
                        'convoId': conversation['convoId'],
                        'name': conversation['name'],
                        'timestamp': conversation['timestamp'],
                        'matching_translation': {
                            'translationText': translation.get('translationText'),
                            'translated': translation.get('translated')
                        }
                    })
                    found_match = True
                    break  # Stop checking other translations in this conversation
            
            if found_match:
                continue  # Move to next conversation
    
        # Prepare the response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # For CORS support
            },
            'body': json.dumps(matching_conversations)
        }
        
        return response
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'event': event  # Include the event for debugging
            })
        }
