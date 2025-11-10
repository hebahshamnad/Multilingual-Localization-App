import json
import boto3
import base64
from decimal import Decimal

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

BUCKET_NAME = 'your_bucket_name'
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
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
        context_id = event['queryStringParameters'].get('id')
        
        if not context_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Brand context ID required'})
            }
        
        response = table.get_item(Key={'id': context_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Brand context not found'})
            }
        
        # Convert Decimal objects to float for JSON serialization
        item = json.loads(json.dumps(response['Item'], default=lambda x: float(x) if isinstance(x, Decimal) else x))
        
        # Fetch file contents from S3 if files exist
        if item.get('files'):
            for file_info in item['files']:
                try:
                    s3_key = file_info['url']
                    
                    # Get file from S3
                    s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
                    file_bytes = s3_response['Body'].read()
                    
                    # Convert to base64 for frontend
                    file_info['content'] = base64.b64encode(file_bytes).decode('utf-8')
                    
                except Exception as e:
                    print(f"Error fetching file {file_info.get('name', 'unknown')}: {str(e)}")
                    file_info['content'] = None
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(item)
        }
    except Exception as e:
        r