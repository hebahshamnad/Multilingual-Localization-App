import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BrandContexts')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}
    
    try:
        username = event['queryStringParameters'].get('username', 'User')
        
        response = table.query(
            IndexName='username-index',
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={':username': username}
        )
        
        items = [{'id': item['id'], 'name': item['name'], 'createdAt': item['createdAt']} 
                for item in response['Items']]
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }