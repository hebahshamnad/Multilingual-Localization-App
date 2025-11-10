import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    try:
        # Parse the incoming request
        if 'body' in event and isinstance(event['body'], dict):
            body = event['body']
        elif 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event
        
        source_language = body.get('sourceLanguage', 'English')
        target_language = body.get('targetLanguage', 'Spanish')
        target_region = body.get('targetRegion', 'United States')
        brand_context = body.get('brandContext', '')
        translation_text = body.get('translationText', '')
        file_contents = ''  # Ensure file contents is empty
        convo_id = body.get('convoId')
        username = body.get('username', 'User')
        previous_translation = body.get('previousTranslation', '')
        
        
        # Calling Bedrock for initial translation
        translated_text = mock_translate(translation_text, target_language,target_region,brand_context,previous_translation)
        
        if translated_text == "error":
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'error'})
            }
        
        adaptation_reason = generate_adaptation_reason(translation_text, translated_text, target_language, target_region)
        back_translation = aws_translate_text(translated_text, target_language, source_language)
        
        # Prepare response data
        response_data = {
            'original': translation_text,
            'translated': translated_text,
            'reason': adaptation_reason,
            'backTranslation': back_translation
        }
        
        # Store in DynamoDB
        stored_convo_id = store_translation_data({
            'sourceLanguage': source_language,
            'targetLanguage': target_language,
            'targetRegion': target_region,
            'brandContext': brand_context,
            'translationText': translation_text,
            'fileContents': file_contents,
            'result': response_data,
            'convoId': convo_id,
            'username': username
        })
        
        # Add conversation ID to response
        response_data['convoId'] = stored_convo_id
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_data)
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
                'message': 'Translation failed'
            })
        }

def mock_translate(text, target_language,target_region,brand_context,previous_translation=''):
    """Translate text using Bedrock"""
    bedrock = boto3.client('bedrock-runtime')
  
    prompt_parts = [
        
        f""" 
  
    Provide a culturally-adapted translation for:

    Input Text: {text}
    Target Language: {target_language} 
    Target Region: {target_region}
    Brand Context: {brand_context}

    Strict Requirements:
    - Translate the text accurately to target language but DO NOT perform word-for-word translation
    - Maintain original meaning and brand voice appropriately as provided in brand context
    - Do not sound robotic, make it human
    - Adapt idioms to local equivalents
    - Use region-appropriate vocabulary (if language seems to be spoken there)
    - Consider local cultural sensitivities
    - Adjust formality level for target region    
    - Preserve any special characters and paragraph breaks where appropriate
"""
    ]
    
    if previous_translation:
        prompt_parts.append(f"""
        Previous Translation (AVOID this approach): {previous_translation}

        Additional Guidelines for New Translation:
        - Create a completely fresh translation that takes a different approach
        - Avoid patterns and word choices used in the previous attempt
        - If the previous was too literal, be more idiomatic (or vice versa)

        Please provide a new translation that addresses these points.
            """)

    prompt_parts.append("Return ONLY the translated text with no explanations or additional content")
    
    prompt = "\n".join(prompt_parts)

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 4000,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text'].strip()

def generate_adaptation_reason(original, translated, target_language, target_region):
    """Generate adaptation reasoning using Bedrock"""
    bedrock = boto3.client('bedrock-runtime')
    
    prompt = f"""
Analyze this translation and explain the specific cultural, linguistic, and regional adaptations made for {target_language} speakers in {target_region}. 
Focus on word choices, cultural references, formality levels, or regional expressions that differ from a literal translation.

Original English: {original}
Adapted Translation: {translated}
Provide a clear explanation in English of what parts of the original translation was culturally adapted and why.
Aim for 1 well-structured paragraph (avoiding numbered lists or bullet points) which uses a MAXIMUM of 75 words that concisely explains the adaptations for a specific brand, culture or target region """

# Provide a clear explanation in English (2-3 sentences) PARAGRAPH FORM of what was culturally adapted and why:"""
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 200,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    return result['content'][0]['text'].strip()



def get_next_convo_id(dynamodb):
    """Get next conversation ID by scanning existing conversations"""
    try:
        response = dynamodb.scan(
            TableName='TranslationHistory',
            ProjectionExpression='convo_id'
        )
        
        if 'Items' in response and response['Items']:
            max_id = max([int(item['convo_id']['N']) for item in response['Items']])
            return max_id + 1
        else:
            return 1
    except:
        return 1

def store_translation_data(data):
    """Store translation data in DynamoDB attribute value format"""
    try:
        dynamodb = boto3.client('dynamodb')
        
        convo_id = data.get('convoId')
        
        if convo_id:
            # Append to existing conversation
            print(f"Appending to existing conversation ID: {convo_id}")
            
            # Get existing conversation
            response = dynamodb.get_item(
                TableName='TranslationHistory',
                Key={'convo_id': {'N': str(convo_id)}}
            )
            
            if 'Item' in response:
                existing_translations = response['Item']['translations']['L']
                next_id = len(existing_translations) + 1
                
                # Add new translation
                new_translation = {
                    'M': {
                        'id': {'N': str(next_id)},
                        'source_lang': {'S': data['sourceLanguage']},
                        'target_lang': {'S': data['targetLanguage']},
                        'target_region': {'S': data['targetRegion']},
                        'brand_context': {'S': data['brandContext']},
                        'translation_text': {'S': data['translationText']},
                        'file_contents': {'S': data['fileContents']},
                        'adapted_translation': {'S': data['result']['translated']},
                        'reason': {'S': data['result']['reason']},
                        'back_translation': {'S': data['result']['backTranslation']}
                    }
                }
                
                existing_translations.append(new_translation)
                
                # Update the conversation
                dynamodb.update_item(
                    TableName='TranslationHistory',
                    Key={'convo_id': {'N': str(convo_id)}},
                    UpdateExpression='SET translations = :translations',
                    ExpressionAttributeValues={':translations': {'L': existing_translations}}
                )
                
                print(f"Successfully appended translation to conversation {convo_id}")
                return convo_id
        
        # Create new conversation
        convo_id = get_next_convo_id(dynamodb)
        print(f"Generated conversation ID: {convo_id}")
        
        new_conversation = {
            'convo_id': {'N': str(convo_id)},
            'convo_name': {'S': f'Session {convo_id}'},
            'user_name': {'S': data.get('username', 'User')},
            'timestamp': {'S': datetime.utcnow().isoformat()},
            'translations': {
                'L': [{
                    'M': {
                        'id': {'N': '1'},
                        'source_lang': {'S': data['sourceLanguage']},
                        'target_lang': {'S': data['targetLanguage']},
                        'target_region': {'S': data['targetRegion']},
                        'brand_context': {'S': data['brandContext']},
                        'translation_text': {'S': data['translationText']},
                        'file_contents': {'S': data['fileContents']},
                        'adapted_translation': {'S': data['result']['translated']},
                        'reason': {'S': data['result']['reason']},
                        'back_translation': {'S': data['result']['backTranslation']}
                    }
                }]
            }
        }
        
        dynamodb.put_item(
            TableName='TranslationHistory',
            Item=new_conversation
        )
        
        print(f"Successfully created conversation with ID: {convo_id}")
        return convo_id
        
    except Exception as e:
        print(f"Error storing to DynamoDB: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return None

# For actual AWS Translate integration, use this function:
def aws_translate_text(text, source_lang, target_lang):
    """
    Actual AWS Translate integration
    """
    translate_client = boto3.client('translate')
    
    # Map language names to AWS Translate codes
    lang_codes = {
        'English': 'en', 'Spanish': 'es', 'French': 'fr', 
        'German': 'de', 'Italian': 'it', 'Portuguese': 'pt'
    }
    
    source_code = lang_codes.get(source_lang, 'auto')
    target_code = lang_codes.get(target_lang, 'en')
    
    response = translate_client.translate_text(
        Text=text,
        SourceLanguageCode=source_code,
        TargetLanguageCode=target_code
    )
    
    return response['TranslatedText']