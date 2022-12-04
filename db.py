import boto3
from botocore.exceptions import ClientError
import mysql.connector
import json


def get_secret():
    secret_name = "mydatabase/secret"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


def create_table():
    secret = get_secret()

    cnx = mysql.connector.connect(
        user=secret["username"],
        password=secret["password"],
        host=secret["host"],
        database=secret["dbname"]
    )
    cursor = cnx.cursor()

    with open("schema.sql", 'r') as fd:
        sqlFile = fd.read()
        cursor.execute(sqlFile)
        cnx.commit()

    cursor.close()
    cnx.close()


if __name__ == "__main__":
    create_table()
