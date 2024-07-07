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
    
def check_file_exists(file_name: str, bucket_name: str):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=file_name)
        print(f"File {file_name} exists in {bucket_name}")
        return True
    except Exception as e:
        print(f"File {file_name} does not exist in {bucket_name}: {e}")
        return False

def download_from_bucket(output_path: str, file_name: str, bucket_name: str):
    with open(output_path, 'wb') as f:
        try:
            s3_client.download_fileobj(bucket_name, file_name, f)
            print(f"File downloaded successfully to {output_path}")
        except Exception as e:
            print(f"Error downloading file from {bucket_name}/{file_name}: {e}")
            raise e

def get_presigned_url(file_name: str, bucket_name: str):
    try:
        url = s3_client.generate_presigned_url('get_object', 
            Params={'Bucket': bucket_name, 'Key': file_name}, 
            ExpiresIn=3600)
        print(f"Presigned URL generated successfully: {url}")
        return url
    except Exception as e:
        print(f"Error generating presigned URL for {bucket_name}/{file_name}: {e}")
        raise e
    
def get_url(file_name: str, bucket_name: str):
    return f"https://{bucket_name}.s3.ap-southeast-2.amazonaws.com/{file_name}"