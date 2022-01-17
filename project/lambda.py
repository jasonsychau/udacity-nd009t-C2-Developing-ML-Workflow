### Lamdba Function #1 Serialize Data

import json
import boto3
import base64
import urllib

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    bucket = event['s3_bucket']
    key = urllib.parse.unquote_plus(event['s3_key'], encoding='utf-8')
    s3_input_uri = "/".join([bucket, key])

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    input_bucket = s3_input_uri.split('/')[0]
    input_object = '/'.join(s3_input_uri.split('/')[1:])
    file_name = '/tmp/image.png'
    s3.download_file(input_bucket, input_object, file_name)

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

### Lambda Function #2 Classify

import json
import base64
import boto3
runtime = boto3.client('runtime.sagemaker')

# from sagemaker.predictor import Predictor
# from sagemaker.serializers import IdentitySerializer

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2022-01-16-16-45-13-169' ## TODO: fill in

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['image_data'])## TODO: fill in

    # Instantiate a Predictor
    # predictor = Predictor(ENDPOINT) ## TODO: fill in

    # For this model the IdentitySerializer needs to be "image/png"
    # predictor.serializer = IdentitySerializer("image/png")
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType='image/png',
        Body=image)

    # Make a prediction:
    # inferences = predictor.predict(image)## TODO: fill in

    # We return the data back to the Step Function    
    event["inferences"] = json.loads(response['Body'].read().decode("utf-8"))
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

### Lambda Function #3 Filter

import json


THRESHOLD = .93


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['inferences'] ## TODO: fill in

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD ## TODO: fill in

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

