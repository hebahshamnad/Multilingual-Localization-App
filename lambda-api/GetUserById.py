

import json
import boto3
from decimal import Decimal

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    try:
        # Get username from query parameters
        if not event.get('queryStringParameters') or not event['queryStringParameters'].get('username'):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Username parameter is required'})
            }
        
        username = event['queryStringParameters']['username']
        
        # Query the username index
        response = table.query(
            IndexName='Username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={
                ':username': username
            }
        )
        
        # Check if user was found
        if response['Items']:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps(response['Items'][0], cls=DecimalEncoder)
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': json.dumps({'error': 'User not found'})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
