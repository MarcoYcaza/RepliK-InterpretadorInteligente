#!/usr/bin/env python3
import os
import boto3


AWS_ACCESS_KEY_ID='AKIA37P6XBSQBEZGLZWT'
AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME='documents-replik'
AWS_S3_REGION_NAME='us-west-2'

s3 =boto3.resource(service_name='s3',region_name=AWS_S3_REGION_NAME,aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

s3.Bucket(AWS_STORAGE_BUCKET_NAME).download_file(Key='csvDump/output.json', Filename='output.json')

