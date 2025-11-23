# Serverless Image Processing Pipeline

## Overview
This project implements a serverless image resizing pipeline using AWS services:
- Amazon S3 (original images and resized images)
- AWS Lambda (image resizing using Pillow)
- AWS Step Functions (orchestration)
- Amazon API Gateway (trigger the workflow)
- CloudWatch (monitoring and logs)

## Architecture
API Gateway → Step Functions → Lambda → S3  
(CloudWatch for logs)

## Repo layout
See project root for `lambda/`, `stepfunctions/`, `api_gateway/`, and `demo/`.

## Prerequisites
- An AWS account with permissions to create S3, Lambda, Step Functions, API Gateway, IAM roles.
- (Region tested): ca-central-1
- Python 3.9 runtime used with a Pillow layer in ca-central-1:
  `arn:aws:lambda:ca-central-1:770693421928:layer:Klayers-p39-pillow:1`

## Deployment (manual steps)
1. Create two S3 buckets:
   - `original-images` (or your chosen name) — store uploaded images
   - `resizes-image` — destination for thumbnails

2. Create the Lambda function:
   - Runtime: Python 3.9
   - Name: `resize-image`
   - Add the Pillow layer (ARN above) via Layers → Specify an ARN
   - Paste `lambda/resize_image/lambda_function.py` into the inline code editor or upload as zip
   - Set memory to 512 MB and timeout 30s (recommended)
   - Attach an execution role that allows `s3:GetObject` on original bucket and `s3:PutObject` on `resizes-image`, plus CloudWatch logs

3. Create the Step Functions state machine:
   - Use the JSON in `stepfunctions/image_state_machine.json`
   - When asked, allow Step Functions to invoke the Lambda (grant permission)

4. Create API Gateway (REST API):
   - Create resource `/resize` with POST method
   - Integration type: AWS Service → Step Functions → Action `StartExecution`
   - Create (or choose) the execution role that has `AmazonAPIGatewayPushToCloudWatchLogs` and an inline policy for `states:StartExecution` on the state machine ARN
   - In Integration Request → add Mapping Template `application/json` with:
     ```
     {
       "stateMachineArn": "YOUR_STATE_MACHINE_ARN",
       "input": "$util.escapeJavaScript($input.body)"
     }
     ```
   - Deploy API to stage `pimageresizeproduction`
   - Final endpoint: `https://{api_id}.execute-api.ca-central-1.amazonaws.com/imageresizeproduction/resize`

5. Test:
   - Upload an image to the original bucket, e.g., `dog.png`
   - POST to the endpoint with body:
     ```json
     {""bucket": "images-orginal","key": "dog.png""}
     ```
   - Confirm a thumbnail appears in `resizes-image` with key `thumbnail-dog.png`
