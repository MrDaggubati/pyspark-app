# Import MinIO library.
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import random, string
 

class Storeitminio:
    """
    stores into a local minio objectstore 
    """
    hostname=$MINIO_HOSTURL

    def mintest():
        
        try:
            # Initialize minioClient with an endpoint and access/secret keys.
            minioClient = Minio(hostname,
                    access_key='AKIAIdfdfdsdfcaOSFODNN7EXAMPLE',
                    secret_key='wJalrXUtnFerererewerererwewefwerEMIER/K7MDENG/bPxRfiCYEXAMPLEKEY',
                    secure=False)

            print('testing if this loads into minio local obect store on docker container')
            x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            print( "check a bucket should be there in minio",x)
            minioClient.make_bucket(x.lower())
            print('yanked')
        except Exception as funcked:
            print('you got funcked',funcked)
            raise
        
