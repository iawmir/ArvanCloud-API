import logging
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)


# connect to arvan storage
try:
    s3_client = boto3.client(
        's3',
        # for dev only
    )
    s3_resource = boto3.resource(
        's3',
        # for dev only
    )
except Exception as exc:
    logging.info(exc)


# check existing bucket and print name
try:
    response = s3_client.list_buckets()
    logging.info('Existing buckets:')
    for bucket in response['Buckets']:
        bucket_name = bucket["Name"]
        logging.info(f'bucket_name: {bucket_name}')

        # check existing user permission and print them
        try:
            bucket_acl = s3_resource.BucketAcl(bucket_name)
            logging.info(bucket_acl.grants)
        except ClientError as e:
            logging.error(e)

        # activate versioning
        try:
            bucket_versioning = s3_resource.Bucket(bucket_name).Versioning()
            bucket_versioning.enable()
            logging.info(bucket_versioning.status)
        except ClientError as e:
            logging.error(e)

        # cors check
        try:
            response = s3_client.get_bucket_cors(Bucket=bucket_name)
            logging.info(response['CORSRules'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
                try:
                    cors_configuration = {
                    'CORSRules': [{
                            'AllowedHeaders': ['Authorization', 'x-custom-header'],
                            "AllowedMethods": [
                                "PUT",
                                "POST",
                                "DELETE"
                            ],
                            'AllowedOrigins': ['*.tmoeini.com','*.taha.one'],
                            "ExposeHeaders": [],
                            'MaxAgeSeconds': 3000
                        }]
                    }
                    
                    response = s3_client.put_bucket_cors(
                        Bucket=bucket_name,
                        CORSConfiguration=cors_configuration
                    )
                    logging.info(response)
                except ClientError as e:
                    logging.error(e)
            else:
                # AllAccessDisabled error == bucket not found
                logging.error(e)
except ClientError as exc:
        logging.error(exc)
