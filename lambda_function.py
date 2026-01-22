import boto3
import string
import random

secrets_client = boto3.client('secretsmanager')

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))

def lambda_handler(event, context):
    secret_name = "MyApp/DBPassword"

    # Get current secret value
    current_secret = secrets_client.get_secret_value(SecretId=secret_name)
    
    # Generate new password
    new_password = generate_password()

    # Update the secret with new password
    secrets_client.put_secret_value(
        SecretId=secret_name,
        SecretString=f'{{"password": "{new_password}"}}'
    )

    return {
        "status": "success",
        "new_password": new_password
    }
