import json
import boto3
import base64
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table('BrandContexts')

ALLOWED_EXTENSIONS = ['.txt', '.doc', '.docx']
BUCKET_NAME = 'your_bucket_name'

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers}
    
    try:
        body = json.loads(event['body'])
        name = body.get('name')
        text = body.get('text', '')
        files = body.get('files', [])
        username = body.get('username', 'User')
        
        if not name or (not text and not files):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Name and content required'})
            }
        
        context_id = str(int(datetime.now().timestamp() * 1000))
        file_urls = []
        
        # Upload files to S3
        for file_data in files:
            file_name = file_data['name']
            file_ext = '.' + file_name.split('.')[-1].lower()
            
            if file_ext not in ALLOWED_EXTENSIONS:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'File type {file_ext} not allowed. Only TXT, DOC, DOCX files are supported.'})
                }
            
            if file_data.get('content'):
                key = f'{username}/{context_id}/{file_name}'
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=key,
                    Body=base64.b64decode(file_data['content']),
                    ContentType=file_data.get('type', 'application/octet-stream')
                )
                
                file_urls.append({
                    'name': file_name,
                    'url': key,
                    'size': file_data.get('size', 0)
                })
        
        # Save to DynamoDB
        item = {
            'id': context_id,
            'username': username,
            'name': name,
            'text': text,
            'files': file_urls,
            'createdAt': datetime.now().isoformat()
        }
        
        table.put_item(Item=item)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'id': context_id, 'message': 'Brand context saved'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }