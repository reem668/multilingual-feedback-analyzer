import boto3
import uuid
import os

from urllib.parse import unquote_plus

s3 = boto3.client('s3')
translate = boto3.client('translate')
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

TABLE_NAME = 'FeedbackTable'
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

# Define keywords per department
department_keywords = {
    "support": ["help", "support", "assistance", "customer service"],
    "sales": ["buy", "purchase", "price", "discount", "product"],
    "delivery": ["shipping", "delivery", "package", "courier", "arrived"],
    "technical": ["error", "bug", "crash", "issue", "technical"]
}

def classify_department(text):
    lower_text = text.lower()
    for dept, keywords in department_keywords.items():
        for word in keywords:
            if word in lower_text:
                return dept
    return "general"

def lambda_handler(event, context):
    try:
        # 1. Get file info from S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = unquote_plus(event['Records'][0]['s3']['object']['key'])

        # 2. Read text from file
        response = s3.get_object(Bucket=bucket, Key=key)
        text = response['Body'].read().decode('utf-8').strip()

        if not text:
            print("Empty file, skipping.")
            return {'statusCode': 200, 'body': 'Empty file'}

        # 3. Detect language
        lang_response = comprehend.detect_dominant_language(Text=text)
        lang_code = lang_response['Languages'][0]['LanguageCode']

        # 4. Translate if needed
        translated = text
        if lang_code != 'en':
            translated = translate.translate_text(
                Text=text,
                SourceLanguageCode=lang_code,
                TargetLanguageCode='en'
            )['TranslatedText']

        # 5. Detect sentiment
        sentiment_response = comprehend.detect_sentiment(Text=translated, LanguageCode='en')
        sentiment = sentiment_response['Sentiment']

        # 6. Classify department
        department = classify_department(translated)
        print(f"Detected department: {department}")

        # 7. Act based on sentiment
        if sentiment.upper() == 'NEGATIVE':
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=(
                    f"🚨 Negative Feedback in [{department.upper()}] Department:\n\n"
                    f"Original: {text}\n\nTranslated: {translated}"
                ),
                Subject=f'Negative Feedback - {department.capitalize()}'
            )
        else:
            table = dynamodb.Table(TABLE_NAME)
            table.put_item(Item={
                'id': str(uuid.uuid4()),
                'original_text': text,
                'translated_text': translated,
                'sentiment': sentiment,
                'language': lang_code,
                'department': department
            })

        return {'statusCode': 200, 'body': 'Processed successfully'}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': 'Internal error'}
