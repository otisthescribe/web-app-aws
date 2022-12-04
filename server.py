import boto3
from botocore.exceptions import ClientError
import mysql.connector
import json
from flask import Flask, render_template, request

app = Flask(__name__)


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


secret = get_secret()


@app.route("/", methods=['GET', 'POST'])
def homepage_get():
    cnx = mysql.connector.connect(
        user=secret["username"],
        password=secret["password"],
        host=secret["host"],
        database=secret["dbname"]
    )
    cursor = cnx.cursor()

    if request.method == 'POST':
        # Add record to the database
        try:
            fname = request.form["firstname"]
            lname = request.form["lastname"]
            age = request.form["age"]
            if fname.isalpha() and lname.isalpha() and age.isnumeric():
                sql = "INSERT INTO Users (FirstName, LastName, Age) VALUES (%s, %s, %s)"
                cursor.execute(sql, [fname, lname, int(age)])
                cnx.commit()
            else:
                raise Exception
        except Exception:
            pass

    cursor.execute("SELECT UserID, FirstName, LastName, Age FROM Users;")
    people = cursor.fetchall()

    cursor.close()
    cnx.close()
    return render_template('index.html', people=people)