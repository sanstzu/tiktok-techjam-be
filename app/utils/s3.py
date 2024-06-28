import boto3
import app.config.aws as config

s3_client = boto3.client('s3', 
            aws_access_key_id=config.AWS_ACCESS_KEY_ID, 
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)

def upload_to_bucket(path: str, file_name:str, bucket_name: str):
    try:
        s3_client.upload_file(path, bucket_name, file_name)
        print(f"File uploaded successfully to {bucket_name}/{file_name}")
    except Exception as e:
        print(f"Error uploading file to {bucket_name}/{file_name}: {e}")
        raise e

def download_from_bucket(output_path: str, file_name: str, bucket_name: str):
    with open(output_path, 'wb') as f:
        try:
            s3_client.download_fileobj(bucket_name, file_name, f)
            print(f"File downloaded successfully to {output_path}")
        except Exception as e:
            print(f"Error downloading file from {bucket_name}/{file_name}: {e}")
            raise e