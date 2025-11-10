import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Get convo_id from query parameters - required
        query_params = event.get('queryStringParameters') or {}
        convo_id = query_params.get('convo_id')
        
        if not convo_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'convo_id parameter is required'})
            }
        
        dynamodb = boto3.client('dynamodb')
        
        # Get specific conversation by convo_id
        response = dynamodb.get_item(
            TableName='TranslationHistory',
            Key={'convo_id': {'N': convo_id}}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Conversation not found'})
            }
        
        item = response['Item']
        convo_name = item['convo_name']['S']
        timestamp = item['timestamp']['S']
        translations = item['translations']['L']
        
        conversation = {
            'convoId': convo_id,
            'name': convo_name,
            'timestamp': timestamp,
            'translations': [
                {
                    'id': t['M']['id']['N'],
                    'sourceLanguage': t['M']['source_lang']['S'],
                    'targetLanguage': t['M']['target_lang']['S'],
                    'targetRegion': t['M']['target_region']['S'],
                    'brandContext': t['M']['brand_context']['S'],
                    'translationText': t['M']['translation_text']['S'],
                    'translated': t['M']['adapted_translation']['S'],
                    'reason': t['M']['reason']['S'],
                    'backTranslation': t['M']['back_translation']['S']
                } for t in translations
            ]
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(conversation)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to fetch conversation'
            })
        }