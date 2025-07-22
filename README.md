
# Multilingual Feedback Analyzer

This project is a serverless AWS-powered web app that allows users to upload feedback files in any language. It auto-translates the content, analyzes the sentiment, extracts the relevant department, and stores the result in DynamoDB. If the feedback is negative, it triggers an alert via SNS.

---

## 🌍 Features

- Upload `.txt` files from a static website
- Auto-translate feedback using Amazon Translate
- Analyze sentiment using Amazon Comprehend
- Extract keywords to determine department
- Store results in DynamoDB
- Send alerts for negative feedback via SNS

---

## ⚙️ Architecture

- **Frontend:** Static website hosted on S3 with file upload via API Gateway (presigned URL)
- **Lambda 1:** `generate_presigned_url.py` – returns a presigned URL to upload to S3
- **Lambda 2:** `process_feedback.py` – triggered by S3 to process the uploaded file
- **Services:** S3, Lambda, API Gateway, DynamoDB, Translate, Comprehend, SNS

---

## 🧠 Tech Stack

- HTML/CSS (Static Web Page)
- AWS Lambda (Python 3.9)
- Amazon S3 (File storage + static hosting)
- API Gateway (REST endpoint)
- Amazon Translate & Comprehend
- Amazon DynamoDB
- Amazon SNS




