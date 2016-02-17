"""
author: Kostas Stamatiou
contact: kostas.stamatiou@digitalglobe.com

Functions to interface with GBDX API.
"""

import os
import json
import requests
from boto import s3


def read_json(json_file):
    """Creates a dictionary from a json file.

    Args:
        json_file (str): A filename ending in .json.

    Returns:
        Dictionary corresponding to json_file (dict)
    """

    def deunicodify_hook(pairs):
        """This is an auxiliary function for reading in ascii.
        """
        new_pairs = []
        for key, value in pairs:
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            new_pairs.append((key, value))
        return dict(new_pairs)

    dictionary = json.load(open(json_file, 'r'), 
                           object_pairs_hook = deunicodify_hook)

    return dictionary


def get_access_token(username, password, api_key):
    """Returns a GBDX access token from user GBDX credentials.
       The access token is good for 7 days.

    Args:
        username (str): GBDX user name.
        password (str): GBDX password.
        api_key (str): GBDX API key.

    Returns:
        GBDX access token (str)
    """

    # get access token
    print "Authenticating on GBDX..."

    url = "https://geobigdata.io/auth/v1/oauth/token/"
    headers = {"Authorization": "Basic %s" % api_key}
    body = {"grant_type":"password", "username": username, "password": password}
    r = requests.post(url, headers=headers, data=body)
    access_token = r.json()["access_token"]

    print "Obtained access token " + access_token

    return access_token


def order_imagery(image_catalog_ids, access_token):
    """Orders images from GBDX.

    Args: 
        image_catalog_ids (list): A list of image catalog ids.
        access_token (str): GBDX access token string.
    
    Returns:
        sales order number (str).
    """

    # hit ordering api
    print "Place order..."
    url = "https://geobigdata.io/orders/v1/"
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    r = requests.post(url, headers=headers, json=image_catalog_ids)     
    sales_order_number = r.json()[0]["salesOrderNumber"]

    print "Order " + str(sales_order_number) + ' placed'
    return sales_order_number


def check_order_status(sales_order_number, access_token):
    """Checks imagery order status.

    Args:
        sales_order_number (str): Sales order number.        
        access_token (str): GBDX access token.

    Returns:
        'done' if imagery has been ordered; 'processing' if not (str).
    """
        
    print "Get status of order " + sales_order_number
    url = "https://geobigdata.io/orders/v1/status/"
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    r = requests.get(url + sales_order_number, headers=headers)
    lines = r.json()["lines"]
    status = "done"
    for line in lines:
        if line["lineItemStatus"] == "DELIVERED":
            continue
        else:
            status = "processing"
    
    print "Order " + sales_order_number + ": " + status

    return status 


def launch_workflow(workflow, access_token):
    """Launches GBDX workflow.

    Args:
        workflow (dict): Dictionary specifying workflow tasks.
        access_token (str): GBDX access token.

    Returns:
        Workflow id (str).
    """

    # hit workflow api
    url = 'https://geobigdata.io/workflows/v1/workflows'
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    try:
        r = requests.post(url, headers = headers, json = workflow)
        workflow_id = r.json()["id"]
        print "Workflow " + str(workflow_id) + " placed"
        return workflow_id
    except TypeError:
        print 'Workflow not launched!'


def check_workflow_status(workflow_id, access_token):
    """Checks workflow status.

    Args:
        workflow_id (str): Workflow id.
        access_token (str): GBDX access token.

    Returns:
        Workflow status (str).
    """
    print 'Get status of workflow: ' + workflow_id
    url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id 
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    r = requests.get(url, headers = headers)

    return r.json()['state']


def has_this_been_ordered(image_catalog_id, access_token):
    """Checks if image has been ordered.

    Args:
        image_catalog_id (str): Image Catalog id in DG factory.
        access_token (str): GBDX access token.
    
    Returns:
        'True' if image has been ordered; 'False' if not (str).
    """
    print 'Check if ' + image_catalog_id + ' has been ordered'
    url = 'https://geobigdata.io/catalog/v1/traverse?includeRelationships=False'
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    body = {"rootRecordId": image_catalog_id, "maxdepth":2, 
            "direction":"both", 
            "labels": ["_fulfillsPartOf", "_acquisition", "_imageFiles"]}
    r = requests.post(url, headers=headers, json=body)
    try:
        productLevel = r.json()['results'][1]['properties']['productLevel']
        if productLevel == 'LV1B':
            return 'True'
        else:
            return 'False'
    except TypeError:
        return 'False'          


def get_location_of_ordered_imagery(sales_order_number, access_token):
    """Find location of ordered imagery.

    Args:
        sales_order_number (str): Sales order number.
        access_token (str): GBDX access token.
    
    Returns:
        Imagery location in S3 (str). 
    """

    url = "https://geobigdata.io/catalog/v1/traverse"
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    body = {"rootRecordId": sales_order_number, "maxdepth": 2, 
            "direction": "both", "labels": ["_fulfillsPartOf", "_imageFiles"]}
    r = requests.post(url, headers=headers, json=body)
    try:
        s3_bucket = r.json()["results"][2]["properties"]["bucketName"]
        s3_prefix_all = r.json()["results"][2]["properties"]["objectIdentifier"]
        s3_prefix = s3_prefix_all.split('/')[0] 
        return 'https://' + s3_bucket + '/' + s3_prefix
    except TypeError:
        print 'Imagery has probably not been delivered'


def launch_aop_to_s3_workflow(input_images_location, 
                              output_images_location,
                              access_token,
                              enable_acomp = "false",
                              enable_dra = "false",
                              ortho_epsg = "EPSG:4326",
                              enable_pansharpen = "false"):

    """Launch aop_to_s3 workflow with choice of select parameters. There
       are more parameter choices to this workflow than the ones provided 
       by this function. In this case, use the more general 
       launch_workflow function. 

       Args:
           input_images_location (str): Imagery location on S3.
           output_images_location (str): Output imagery location on S3.
           enable_acomp (str): Apply ACOMP; "true" or "false".
           enable_dra (str): Apply dynamic range adjustment; "true" or "false".
           ortho_epsg (str): Choose projection.
           enable_pansharpen (str): Apply pansharpening; "true" or "false".

       Returns:
           Workflow id (str).
    """

    # create workflow dictionary
    aop_to_s3 = json.loads("""{
    "tasks": [{
        "containerDescriptors": [{
            "properties": {"domain": "raid"}}],
        "name": "AOP",
        "inputs": [{
            "name": "data",
            "value": "INPUT_BUCKET"
        }, {
            "name": "enable_acomp",
            "value": "false"
        }, {
            "name": "enable_dra",
            "value": "false"
        }, {
            "name": "ortho_epsg",
            "value": "EPSG:4326"
        }, {
            "name": "enable_pansharpen",
            "value": "false"
        }],
        "outputs": [{
            "name": "data"
        }, {
            "name": "log"
        }],
        "timeout": 36000,
        "taskType": "AOP_Strip_Processor",
        "containerDescriptors": [{"properties": {"domain": "raid"}}]
    }, {
        "inputs": [{
            "source": "AOP:data",
            "name": "data"
        }, {
            "name": "destination",
            "value": "OUTPUT_BUCKET"
        }],
        "name": "StageToS3",
        "taskType": "StageDataToS3",
        "containerDescriptors": [{"properties": {"domain": "raid"}}]
    }],
    "name": "aop_to_s3"
    }""")

    aop_to_s3['tasks'][0]['inputs'][0]['value'] = input_images_location
    aop_to_s3['tasks'][0]['inputs'][1]['value'] = enable_acomp
    aop_to_s3['tasks'][0]['inputs'][2]['value'] = enable_dra
    aop_to_s3['tasks'][0]['inputs'][3]['value'] = ortho_epsg
    aop_to_s3['tasks'][0]['inputs'][4]['value'] = enable_pansharpen
    aop_to_s3['tasks'][1]['inputs'][1]['value'] = output_images_location

    # launch workflow
    workflow_id = launch_workflow(aop_to_s3, access_token)

    return workflow_id


def get_s3_info(access_token):
    """Get your assigned GBDX S3 bucket and prefix.

       Args:
           access_token (str): GBDX access token.

       Returns:
           bucket (str): S3 personal bucket
           prefix (str): S3 personal prefix    
    """

    print "Get S3 bucket info"
    url = "https://geobigdata.io/s3creds/v1/prefix?duration=3600"
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    r = requests.get(url, headers=headers)
    results = r.json()
    bucket = r.json()["bucket"]
    prefix = r.json()["prefix"]
    
    return bucket, prefix


def get_s3_credentials(access_token):
    """Get your GBDX S3 credentials.

       Args:
           access_token (str): GBDX access token.

       Returns:
           access_key (str): S3 access key
           secret_key (str): S3 secret key
           session_token (str): S3 session token
    """

    url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
    headers = {"Content-Type": "application/json", 
               "Authorization": "Bearer " + access_token}
    r = requests.get(url, headers=headers)
    results = r.json()

    access_key = results["S3_access_key"]
    secret_key = results["S3_secret_key"]
    session_token = results["S3_session_token"]

    return access_key, secret_key, session_token       


def download_from_s3(s3_bucket, s3_directory, local_directory, access_token):
    """Download files from s3_bucket/s3_directory.

       Args:
           s3_bucket (str): User S3 bucket.
           s3_directory (str): S3 directory within bucket. It should not be 
                               preceded with nor followed by a backslash.
           local_directory (str): Local directory where files will be stored.
           access_token (str): GBDX access token.              
    """

    print 'Getting S3 credentials'
    access_key, secret_key, session_token = get_s3_credentials(access_token)
    
    print 'Connecting to S3'
    s3conn = s3.connect_to_region('us-east-1', aws_access_key_id=access_key, 
                                  aws_secret_access_key=secret_key, 
                                  security_token=session_token)

    b = s3conn.get_bucket(s3_bucket, validate=False, 
                          headers={'x-amz-security-token': session_token})

    whats_in_here = b.list(s3_directory)

    print 'Downloading contents'
    for key in whats_in_here:
        filename = key.name.split('/')[-1]
        print filename
        try:
            res = key.get_contents_to_filename(local_directory + '/' + filename)
        except:
            print 'Could not download this file!'
            pass    

    print 'Done!'


def delete_in_s3(s3_bucket, s3_directory, access_token):
    """Delete all files within s3_bucket/s3_directory.

       Args:
           s3_bucket (str): User S3 bucket.
           s3_directory (str): S3 directory within bucket. It should not be 
                               preceded with nor followed by a backslash.
           access_token (str): GBDX access token. 
    """

    print 'Getting S3 credentials'
    access_key, secret_key, session_token = get_s3_credentials(access_token)
    
    print 'Connecting to S3'
    s3conn = s3.connect_to_region('us-east-1', 
                                  aws_access_key_id=access_key, 
                                  aws_secret_access_key=secret_key, 
                                  security_token=session_token)

    b = s3conn.get_bucket(s3_bucket, validate=False, 
                          headers={'x-amz-security-token': session_token})

    whats_in_here = b.list(s3_directory)

    print 'Deleting contents'

    for key in whats_in_here:
        b.delete_key(key)

    print 'Done!'



