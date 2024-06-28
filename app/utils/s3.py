import boto3
import app.config.aws as config


def upload_to_bucket(path: str, file_name:str, bucket_name: str):
    s3_client = boto3.client('s3', 
                             aws_access_key_id=config.AWS_ACCESS_KEY_ID, 
                             aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
                             )
    try:
        s3_client.upload_file(path, bucket_name, file_name)
        print(f"File uploaded successfully to {bucket_name}/{file_name}")
    except Exception as e:
        print(f"Error uploading file to {bucket_name}/{file_name}: {e}")
        raise e
