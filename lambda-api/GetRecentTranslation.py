import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Get user_name from query parameters - required
        query_params = event.get('queryStringParameters') or {}
        user_name = query_params.get('user_name')
        
        if not user_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'user_name parameter is required'})
            }
        
        dynamodb = boto3.client('dynamodb')
        
        # Scan conversations filtered by user_name
        response = dynamodb.scan(
            TableName='TranslationHistory',
            FilterExpression='user_name = :user_name',
            ExpressionAttributeValues={':user_name': {'S': user_name}},
            ProjectionExpression='convo_id, convo_name, #ts, translations',
            ExpressionAttributeNames={'#ts': 'timestamp'}
        )
        
        conversations = []
        for item in response['Items']:
            convo_id = item['convo_id']['N']
            convo_name = item['convo_name']['S']
            timestamp = item['timestamp']['S']
            translations = item['translations']['L']
            
            # Get the first translation for preview
            if translations:
                first_translation = translations[0]['M']
                source_lang = first_translation['source_lang']['S']
                target_lang = first_translation['target_lang']['S']
                
                conversations.append({
                    'convoId': convo_id,
                    'name': convo_name,
                    'timestamp': timestamp,
                    'sourceLanguage': source_lang,
                    'targetLanguage': target_lang,
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
                })
        
        # Sort by timestamp (most recent first)
        conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(conversations)
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
                'message': 'Failed to fetch translations'
            })
        }