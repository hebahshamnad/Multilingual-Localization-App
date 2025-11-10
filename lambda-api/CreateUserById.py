import json
import boto3
import traceback
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    # Handle OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({})
        }
    
    try:
        # Debug: Print the event structure
        print("Event received:", json.dumps(event))
        
        # Parse request body - handle different event structures
        body = {}
        if isinstance(event.get('body'), str):
            body = json.loads(event.get('body', '{}'))
        elif isinstance(event.get('body'), dict):
            body = event.get('body', {})
        elif event.get('username'):
            # Direct invocation with parameters
            body = event
        
        print("Parsed body:", json.dumps(body))
        
        # Extract user data
        username = body.get('username')
        email = body.get('email')
        name = body.get('name', '')
        
        if not username or not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Username and email are required'})
            }
        
        # Create user profile
        current_date = datetime.now().strftime('%Y-%m-%d')
        user_item = {
            'PK': "USER#"+username,  # Changed from UserId to PK to match table's primary key
            'SK': "PROFILE#"+username,  # Changed from UserId to PK to match table's primary key

            'username': username,
            'email': email,
            'name': name,
            'phone': '-',
            'location': '-',
            'plan': 'Basic',
            'memberSince': current_date,
            'usage': {
                'translations': 0,
                'percentage': 0
            },
            'languages': [
                {'name': 'English', 'level': 'Native', 'flag': 'us'}
            ]
        }
        
        # Save to DynamoDB
        table.put_item(Item=user_item)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'User profile created successfully'})
        }
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error: {str(e)}")
        print(f"Traceback: {error_trace}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }