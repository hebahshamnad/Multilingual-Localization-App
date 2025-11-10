import json
import boto3

def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = body['username']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserProfiles')
    
    response = table.update_item(
        Key={
            'PK': f'USER#{username}',
            'SK': f'PROFILE#{username}'
        },
        UpdateExpression='ADD #u.translations :inc',
        ExpressionAttributeNames={'#u': 'usage'},
        ExpressionAttributeValues={':inc': 1},
        ReturnValues='ALL_NEW'
    )
    
    new_count = response['Attributes']['usage']['translations']
    percentage = new_count / 200
    percentage=percentage*100
    
    table.update_item(
        Key={
            'PK': f'USER#{username}',
            'SK': f'PROFILE#{username}'
        },
        UpdateExpression='SET #u.percentage = :pct',
        ExpressionAttributeNames={'#u': 'usage'},
        ExpressionAttributeValues={':pct': percentage}
    )
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'success': True})
    }