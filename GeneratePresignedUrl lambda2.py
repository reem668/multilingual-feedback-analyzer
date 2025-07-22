import boto3
import os
import urllib.parse

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    try:
        # Get query string filename
        query = event.get('queryStringParameters') or {}
        filename = query.get('filename')

        if not filename or not filename.endswith('.txt'):
            return {
                'statusCode': 400,
                'body': 'Invalid or missing .txt filename'
            }

        key = urllib.parse.quote(filename)

        # Generate presigned URL
        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': BUCKET, 'Key': key, 'ContentType': 'text/plain'},
            ExpiresIn=300
        )

        return {
            'statusCode': 200,
            'headers': { "Access-Control-Allow-Origin": "*" },
            'body': f'{{"uploadUrl": "{url}"}}'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
