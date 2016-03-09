"""
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin
Contact: kostas.stamatiou@digitalglobe.com

Functions to interface with GBDX API.
"""

import json
import os
import sys

from boto import s3
from gbdx_auth import gbdx_auth


class Interface():


    gbdx_connection = None
    def __init__(self):
    # This will throw an exception if your .ini file is not set properly
        self.gbdx_connection = gbdx_auth.get_session()


# ordering API v1 to be deprecated -----------------------------------------

    def order_imagery_v1(self, image_catalog_ids):
        """Orders images from GBDX.

           Args: 
               image_catalog_ids (list): A list of image catalog ids.
        
           Returns:
               sales order number (str).
        """

        # hit ordering api
        print "Orders/v1 is deprecated.... please use orders/v2"
        print "Place order"
        url = "https://geobigdata.io/orders/v1/"

        r = self.gbdx_connection.post(url, json=image_catalog_ids)     
        sales_order_number = r.json()[0]["salesOrderNumber"]

        return sales_order_number


    def has_this_been_ordered_v1(self, image_catalog_id):
        """Checks if image has been ordered.

         Args:
             image_catalog_id (str): Image Catalog id in DG factory.

         Returns:
             'True' if image has been ordered; 'False' if not (str).
        """

        print "Orders/v1 is deprecated.... please use orders/v2"
        print 'Check if ' + image_catalog_id + ' has been ordered'
        url = ('https://geobigdata.io/catalog/v1/'
             'traverse?includeRelationships=False')
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


    def check_order_status_v1(self, sales_order_number):
        """Checks imagery order status.

           Args:
               sales_order_number (str): Sales order number.        

           Returns:
               'done' if imagery has been ordered; 'processing' if not (str).
        """

        print "Orders/v1 is deprecated.... please use orders/v2"    
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

        return status 


    def traverse_request_v1(self, identifier, labels=None, maxdepth=None):
        """Runs a simple catalog traverse for an ID

           Args:       
               identifier (str): Value to search for (rootRecordId).
               labels (list): Object types filter.
               maxdepth (int): Number of relationships to traverse.

           Returns:
               Search Results (dict).
        """

        print "Orders/v1 is deprecated.... please use orders/v2"

        if labels is None:
          labels = ["_acquisition", "_imageFiles", "_fulfillsPartOf"]
        if maxdepth is None:
          maxdepth = 1

        url = ('https://geobigdata.io/catalog/v1/'
             'traverse?includeRelationships=false')
        body = {"rootRecordId": identifier, 
              "maxdepth": maxdepth, 
              "direction": "both", 
              "labels": labels}
        r = self.gbdx_connection.post(url, data=json.dumps(body), verify=False)

        return r


    def get_location_of_ordered_imagery_v1(self,order_id):
        """Find location of ordered imagery.

           Args:
               sales_order_number (str): Sales order number.

           Returns:
               Imagery location in S3 (str). 
        """

        print "Orders/v1 is deprecated.... please use orders/v2"

        url = "https://geobigdata.io/catalog/v1/traverse"
        body = json.dumps({"rootRecordId": order_id, 
                         "maxdepth": 2, 
                         "direction": "both", 
                         "labels": ["_fulfillsPartOf", "_imageFiles"]})
        r = self.gbdx_connection.post(url, data=body)
        print r.json()
        try:
          results = r.json()["results"][2]["properties"]
          s3_bucket = results["bucketName"]
          s3_prefix_all = results["objectIdentifier"]
          s3_prefix = s3_prefix_all.split('/')[0] 
          return 'https://' + s3_bucket + '/' + s3_prefix
        except TypeError:
          print 'Imagery has probably not been delivered'


# end: ordering API v1 to be deprecated ---------------------------------------


    def order_imagery(self, image_catalog_ids):
        """Orders images from GBDX.

           Args: 
               image_catalog_ids (list or string): A list of image catalog ids 
               or a single image catalog id.

           Returns:
               order_id (str): The ID of the order placed.
        """

        # hit ordering api
        print "Place order"
        url = "https://geobigdata.io/orders/v2/order/"
        
        # determine if the user inputted a list of image_catalog_ids 
        # or a string of one
        if type(image_catalog_ids).__name__=='list':
            r = self.gbdx_connection.post(url, 
                                          data=json.dumps(image_catalog_ids)) 
        else:
            r = self.gbdx_connection.post(url, 
                                          data=json.dumps([image_catalog_ids]))
        
        order_id = r.json().get("order_id", {})

        return order_id


    def check_order_status(self, order_id):
        """Checks imagery order status.  There can be more than one image per 
           order and this function returns the status of all images 
           within the order.

           Args:
               order_id (str): The ID of the order placed.        

           Returns:
               dict (str) with keys = locations of ordered images and 
               values = status of each ordered image.
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
          
        return dict(results)


    def launch_workflow(self, workflow):
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
            return workflow_id
        except TypeError:
            print 'Workflow not launched!'


    def check_workflow_status(self, workflow_id):
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


    def get_task_definition(self, task_name):
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
             enable_dra (str): Apply dynamic range adjust; "true" or "false".
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
      print 'Launch workflow'
      workflow_id = self.launch_workflow(aop_to_s3)

      return workflow_id

    
    def get_s3_info(self):
      """Get user info for GBDX S3.

         Args:
             None.

         Returns: 
             Dictionary with S3 access key, S3 secret key, S3 session token,
             user bucket and user prefix (dict).
      """

      url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
      r = self.gbdx_connection.get(url)
      s3_info = r.json()
      print "Obtained S3 Credentials"

      return s3_info


    def download_from_s3(self, location, local_dir = '.'):
      """Download content from bucket/prefix/location. 
         If location is a directory, all files in the directory are 
         downloaded. If it is a file, then that file is downloaded.

         Args:
             location (str): S3 location within prefix. It should not be 
                             preceded with nor followed by a backslash.
             local_dir (str): Local directory where file(s) will be stored.
                              Default is here.
      """

      print 'Getting S3 info'
      s3_info = self.get_s3_info()
      bucket = s3_info["bucket"]
      prefix = s3_info["prefix"]
      access_key = s3_info["S3_access_key"]
      secret_key = s3_info["S3_secret_key"]
      session_token = s3_info["S3_session_token"]
      
      print 'Connecting to S3'
      s3conn = s3.connect_to_region('us-east-1', aws_access_key_id=access_key, 
                                    aws_secret_access_key=secret_key, 
                                    security_token=session_token)

      b = s3conn.get_bucket(bucket, validate=False, 
                            headers={'x-amz-security-token': session_token})

      whats_in_here = b.list(prefix + '/' + location)

      print 'Downloading contents'
      for key in whats_in_here:
          filename = key.name.split('/')[-1]
          print filename
          res = key.get_contents_to_filename(local_dir + '/' + filename)
          
      print 'Done!'


    def delete_in_s3(self, location):
      """Delete content in bucket/prefix/location. 
         If location is a directory, all files in the directory are 
         deleted. If it is a file, then that file is deleted.

         Args:
             location (str): S3 location within prefix. It should not be 
                             preceded with nor followed by a backslash.
      """

      print 'Getting S3 info'
      s3_info = self.get_s3_info()
      bucket = s3_info["bucket"]
      prefix = s3_info["prefix"]
      access_key = s3_info["S3_access_key"]
      secret_key = s3_info["S3_secret_key"]
      session_token = s3_info["S3_session_token"]
      
      print 'Connecting to S3'
      s3conn = s3.connect_to_region('us-east-1', aws_access_key_id=access_key, 
                                    aws_secret_access_key=secret_key, 
                                    security_token=session_token)

      b = s3conn.get_bucket(bucket, validate=False, 
                            headers={'x-amz-security-token': session_token})

      whats_in_here = b.list(prefix + '/' + location)

      print 'Deleting contents'

      for key in whats_in_here:
          b.delete_key(key)

      print 'Done!'