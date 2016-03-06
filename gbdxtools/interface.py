"""
authors: Kostas Stamatiou, Dan Getman
contact: kostas.stamatiou@digitalglobe.com

Functions to interface with GBDX API.
"""

import os
import json
from boto import s3
import re
from gbdx_auth import gbdx_auth

class Interface():

  gbdx_connection = None
  def __init__(self, **kwargs):
    if kwargs.get('username') and kwargs.get('password') and kwargs.get('client_id') and kwargs.get('client_secret'):
        self.gbdx_connection = gbdx_auth.session_from_kwargs(**kwargs)
    else:
      # This will throw an exception if your .ini file is not set properly
      self.gbdx_connection = gbdx_auth.get_session()

  def get_s3tmp_cred(self):
      """Request temporary credentials for the GBDX S3 Storage Service
         The access token is good for 10 hours.

         Args:
             None.

         Returns: 
             Set of credentials needed to access S3 Storage (dict).
      """
      url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
      r = self.gbdx_connection.get(url)
      s3tmp_cred = r.json()
      print "Obtained S3 Credentials"

      return s3tmp_cred


  def s3tmp_cred_reg(self,s3_cred):
      """Modify the local .aws/credentials file so that it has the current credentials.

         Args:
             S3 Credentials (dict): Set of credentials needed to access S3 Storage.

         Returns:
             Indicator of successful action (bool).
      """
      response = False

      # TODO: This has not been tested on a fresh install or something like a docker. 
      # It may only work after the user has run the aws configure command
      try:
          f1 = open(os.path.join(os.path.expanduser('~'),'.aws/credentials'), 'w+')
          # Write the credentials file
          f1.write("[default]" + '\n')
          f1.write("aws_secret_access_key=" + s3_cred['S3_secret_key'] + '\n')
          f1.write("aws_access_key_id=" + s3_cred['S3_access_key'] + '\n')
          f1.write("aws_session_token=" + s3_cred['S3_session_token'] + '\n')
          f1.close()
          response = True
          print "Stored S3 Credentials Locally"
      except:
          print "Unexpected error:", sys.exc_info()[0]

      return response


  def order_imagery(self,image_catalog_ids):
      """Orders images from GBDX.

         Args: 
             image_catalog_ids (list): A list of image catalog ids.
      
         Returns:
             sales order number (str).
      """

      # hit ordering api
      print "Orders/v1 is deprecated.... please use orders/v2"
      print "Place order..."
      url = "https://geobigdata.io/orders/v1/"

      r = self.gbdx_connection.post(url, json=image_catalog_ids)     
      sales_order_number = r.json()[0]["salesOrderNumber"]

      print "Order " + str(sales_order_number) + ' placed'
      return sales_order_number

  def order_imagery_v2(self,image_catalog_ids):
      """Orders images from GBDX.

         Args: 
             image_catalog_ids (list): A list of image catalog ids.
      
         Returns:
             order_id (str): The ID of the order placed.
      """

      # hit ordering api
      print "Place order..."
      url = "https://geobigdata.io/orders/v2/order/"
      r = self.gbdx_connection.post(url,data=json.dumps(image_catalog_ids))     
      order_id = r.json().get("order_id", {})

      print "Order " + str(order_id) + ' placed'
      return order_id

  def check_order_status(self,sales_order_number):
      """Checks imagery order status.

         Args:
             sales_order_number (str): Sales order number.        

         Returns:
             'done' if imagery has been ordered; 'processing' if not (str).
      """
          
      print "Get status of order " + sales_order_number
      url = "https://geobigdata.io/orders/v1/status/"
      r = self.gbdx_connection.get(url + sales_order_number)
      lines = r.json()["lines"]
      status = "done"
      for line in lines:
          if line["lineItemStatus"] == "DELIVERED":
              continue
          else:
              status = "processing"
      
      print "Order " + sales_order_number + ": " + status

      return status 

  def check_order_status_v2(self,order_id):
      """Checks imagery order status.  There can be more than one image per order and this function returns the 
      status of all images within the order.

         Args:
             order_id (str): The ID of the order placed.        

         Returns:
             dict (str) with keys = locations of ordered images and values = status of each ordered image.
      """
          
      print "Get status of order " + order_id
      url = "https://geobigdata.io/orders/v2/order/"
      r = self.gbdx_connection.get(url + order_id)
      lines = r.json().get("acquisitions", {})
      results = []
      for line in lines:
          location = line['location']
          status = line["state"]
          results.append((location, status))
          
      resultsdict = dict(results)        

      return resultsdict

  def traverse_request(self, identifier, labels=None, maxdepth=None):
      """Runs a simple catalog traverse for an ID

         Args:       
             identifier (str): Value to search for (rootRecordId).
             labels (list): Object types filter.
             maxdepth (int): Number of relationships to traverse.

         Returns:
             Search Results (dict).
      """

      if labels is None:
          labels = ["_acquisition", "_imageFiles", "_fulfillsPartOf"]
      if maxdepth is None:
          maxdepth = 1

      url = 'https://geobigdata.io/catalog/v1/traverse?includeRelationships=false'
      body = {"rootRecordId": identifier, "maxdepth": maxdepth, "direction": "both", "labels": labels}
      r = self.gbdx_connection.post(url, data=json.dumps(body), verify=False)

      return r


  def get_landsat_properties(self, identifier):
      """Queries main properties (Complete S3 Bucket Reference (source), footprintWkt, timestamp, identifier) 
         for a simple catalog traverse on a Landsat CatalogID.
         Return Dict is keyed by image identifier.
         Properties can be added as needed. 

         Args:       
             identifier (str): Value to search for (CatalogID for Landsat Image).

         Returns:
             Image Properties (dict).
      """

      return_set = {}

      results_set = self.traverse_request(identifier, ["_landsatacquisition"], 1).json()

      if "results" in results_set:
          if len(results_set) > 0:
              results_set['results'][0]['properties']['source'] = re.sub('.+?(?=landsat)', 'https://', results_set['results'][0]['properties']['browseURL'])
              results_set['results'][0]['properties']['source'] = re.sub('([^/]+$)', '', results_set['results'][0]['properties']['source'])
              return_set[identifier] = {}
              return_set[identifier]['source'] = results_set['results'][0]['properties']['source']
              return_set[identifier]['footprintWkt'] = results_set['results'][0]['properties']['footprintWkt']
              return_set[identifier]['timestamp'] = results_set['results'][0]['properties']['timestamp']
              return_set[identifier]['identifier'] = results_set['results'][0]['identifier']

      return return_set


  def get_dg_properties(self, sales_order_num):
      """Queries main properties (Complete S3 Bucket Reference (source), footprintWkt, timestamp, identifier) 
         for a simple catalog traverse using a sales order number and filtering to only DG imagery.
         Return Dict is keyed by image identifier.
         Properties can be added as needed.

         Note, if all we want is the bucket, this could also just pull all ObjectStoreData objects and get their buckets.
         This gives us additional details in case we need to filter the parts of each acquisition by footprint.

         Args:       
             sales_order_num (str): Value to search for (Sales Order Number).

         Returns:
             Image Properties (dict).
      """

      return_set = {}

      results_set = self.traverse_request(sales_order_num, ["_acquisition", "_imageFiles", "_fulfillsPartOf"], 1).json()

      if "results" in results_set:
          if len(results_set) > 0:
              for val in results_set['results']:
                  if val['type'] == "DigitalGlobeProduct":
                      if not val['properties']['productCatalogId'] in return_set:
                          return_set[val['properties']['productCatalogId']] = {}

                      return_set[val['properties']['productCatalogId']][val['properties']['bands']] = {
                          'DGPIdentifier': val['identifier'],
                          'productCatalogId': val['properties']['productCatalogId'],
                          'footprintWkt': val['properties']['footprintWkt'],
                          'timestamp': val['properties']['timestamp']
                      }

              for key, val_1 in return_set.iteritems():
                  for key, val_2 in val_1.iteritems():
                      results_set = self.traverse_request(val_2['DGPIdentifier'], ["_acquisition", "_imageFiles", "_fulfillsPartOf"], 1).json()
                      for val_3 in results_set['results']:
                          if val_3['type'] == "ObjectStoreData":
                              val_2['bucket'] = val_3['properties']['bucketName']
                              val_2['objectIdentifier'] = val_3['properties']['objectIdentifier']
                              val_2['source'] = "https://" + val_3['properties']['bucketName'] + "/" + re.search('([^/]+)', val_3['properties']['objectIdentifier']).group(1)

      return return_set


  def launch_workflow(self,workflow):
      """Launches GBDX workflow.

         Args:
             workflow (dict): Dictionary specifying workflow tasks.

         Returns:
             Workflow id (str).
      """

      # hit workflow api
      url = 'https://geobigdata.io/workflows/v1/workflows'
      try:
          r = self.gbdx_connection.post(url, json = workflow)
          workflow_id = r.json()["id"]
          print "Workflow " + str(workflow_id) + " placed"
          return workflow_id
      except TypeError:
          print 'Workflow not launched!'


  def check_workflow_status(self,workflow_id):
      """Checks workflow status.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             Workflow status (str).
      """
      print 'Get status of workflow: ' + workflow_id
      url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id 
      r = self.gbdx_connection.get(url)

      return r.json()['state']

  # This function seems to be redundant with check_order_status_v2.
  def has_this_been_ordered(self,image_catalog_id):
      """Checks if image has been ordered.

         Args:
             image_catalog_id (str): Image Catalog id in DG factory.
      
         Returns:
             'True' if image has been ordered; 'False' if not (str).
      """
      print 'Check if ' + image_catalog_id + ' has been ordered'
      url = 'https://geobigdata.io/catalog/v1/traverse?includeRelationships=False'
      body = json.dumps({"rootRecordId": image_catalog_id, "maxdepth":2, 
              "direction":"both", 
              "labels": ["_fulfillsPartOf", "_acquisition", "_imageFiles"]})
      r = self.gbdx_connection.post(url, data=body)
      
      try:
          productLevel = r.json()['results'][1]['properties']['productLevel']
          if productLevel == 'LV1B':
              return 'True'
          else:
              return 'False'
      except TypeError:
          return 'False'          


  # TODO: Might need to check to see if this works with multiple images in a single order.
  # Also this function seems to be redundant with check_order_status_v2.
  def get_location_of_ordered_imagery(self,order_id):
      """Find location of ordered imagery.

         Args:
             sales_order_number (str): Sales order number.
      
         Returns:
             Imagery location in S3 (str). 
      """

      url = "https://geobigdata.io/catalog/v1/traverse"
      body = json.dumps({"rootRecordId": order_id, "maxdepth": 2, 
              "direction": "both", "labels": ["_fulfillsPartOf", "_imageFiles"]})
      r = self.gbdx_connection.post(url, data=body)
      print r.json()
      try:
          s3_bucket = r.json()["results"][2]["properties"]["bucketName"]
          s3_prefix_all = r.json()["results"][2]["properties"]["objectIdentifier"]
          s3_prefix = s3_prefix_all.split('/')[0] 
          return 'https://' + s3_bucket + '/' + s3_prefix
      except TypeError:
          print 'Imagery has probably not been delivered'


  def get_task_definition(self,task_name):
      """Get task definition.

         Args:
             task_name (str): The task name.

         Return:
             Task definition (dict).
      """

      url = "https://geobigdata.io/workflows/v1/tasks/" + task_name
      r = self.gbdx_connection.get(url)
      
      return r.json()


  def launch_aop_to_s3_workflow(self,
                                input_images_location, 
                                output_images_location,
                                bands = "Auto",
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
             bands (str): Bands to process (choices are "PAN+MS", "PAN", "MS")
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
              "name": "bands",
              "value": "Auto"
          },
             {
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
      aop_to_s3['tasks'][0]['inputs'][1]['value'] = bands
      aop_to_s3['tasks'][0]['inputs'][2]['value'] = enable_acomp
      aop_to_s3['tasks'][0]['inputs'][3]['value'] = enable_dra
      aop_to_s3['tasks'][0]['inputs'][4]['value'] = ortho_epsg
      aop_to_s3['tasks'][0]['inputs'][5]['value'] = enable_pansharpen
      aop_to_s3['tasks'][1]['inputs'][1]['value'] = output_images_location

      # launch workflow
      workflow_id = self.launch_workflow(aop_to_s3)

      return workflow_id


  def get_s3_info(self):
      """Get your assigned GBDX S3 bucket and prefix.

         Args:
             None.

         Returns:
             S3 personal bucket (str), S3 personal prefix (str).    
      """

      print "Get S3 bucket info"
      url = "https://geobigdata.io/s3creds/v1/prefix?duration=3600"
      r = self.gbdx_connection.get(url)
      results = r.json()
      bucket = r.json()["bucket"]
      prefix = r.json()["prefix"]
      
      return bucket, prefix


  def get_s3_credentials(self):
      """Get your GBDX S3 credentials.

         Args:
             None

         Returns:
             S3 access key (str),  S3 secret key (str), S3 session token (str).
      """

      url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
      r = self.gbdx_connection.get(url)
      results = r.json()

      access_key = results["S3_access_key"]
      secret_key = results["S3_secret_key"]
      session_token = results["S3_session_token"]

      return access_key, secret_key, session_token       


  def download_from_s3(self,s3_bucket, s3_directory, local_directory):
      """Download files from s3_bucket/s3_directory.

         Args:
             s3_bucket (str): User S3 bucket.
             s3_directory (str): S3 directory within bucket. It should not be 
                                 preceded with nor followed by a backslash.
             local_directory (str): Local directory where files will be stored.
      """

      print 'Getting S3 credentials'
      access_key, secret_key, session_token = self.get_s3_credentials()
      
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


  def delete_in_s3(self,s3_bucket, s3_directory):
      """Delete all files within s3_bucket/s3_directory.

         Args:
             s3_bucket (str): User S3 bucket.
             s3_directory (str): S3 directory within bucket. It should not be 
                                 preceded with nor followed by a backslash.
      """

      print 'Getting S3 credentials'
      access_key, secret_key, session_token = self.get_s3_credentials()
      
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



