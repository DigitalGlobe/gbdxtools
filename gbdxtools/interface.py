'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters
Contact: kostas.stamatiou@digitalglobe.com

Functions to interface with GBDX API.
'''

import json
import os
import requests

from boto import s3
from gbdx_auth import gbdx_auth
from StringIO import StringIO
from PIL import Image
from pygeoif import geometry
from sympy.geometry import Point, Polygon

import codecs



class Interface():


    gbdx_connection = None
    def __init__(self, **kwargs):
        if (kwargs.get('username') and kwargs.get('password') and 
            kwargs.get('client_id') and kwargs.get('client_secret')):
            self.gbdx_connection = gbdx_auth.session_from_kwargs(**kwargs)
        else:
            # This will throw an exception if your .ini file is not set properly
            self.gbdx_connection = gbdx_auth.get_session()


    def get_s3_info(self):
        '''Get user info for GBDX S3.

           Args:
               None.

           Returns:
               Dictionary with S3 access key, S3 secret key, S3 session token,
               user bucket and user prefix (dict).
        '''

        url = 'https://geobigdata.io/s3creds/v1/prefix?duration=36000'
        r = self.gbdx_connection.get(url)
        s3_info = r.json()
        print 'Obtained S3 Credentials'

        return s3_info
        

    def order_imagery(self, image_catalog_ids):
        '''Orders images from GBDX.

           Args:
               image_catalog_ids (list or string): A list of image catalog ids
               or a single image catalog id.

           Returns:
               order_id (str): The ID of the order placed.
        '''

        # hit ordering api
        print 'Place order'
        url = 'https://geobigdata.io/orders/v2/order/'

        # determine if the user inputted a list of image_catalog_ids
        # or a string of one
        if type(image_catalog_ids).__name__ == 'list':
            r = self.gbdx_connection.post(url,
                                          data=json.dumps(image_catalog_ids))
        else:
            r = self.gbdx_connection.post(url,
                                          data=json.dumps([image_catalog_ids]))

        order_id = r.json().get("order_id", {})

        return order_id


    def check_order_status(self, order_id):
        '''Checks imagery order status.  There can be more than one image per
           order and this function returns the status of all images
           within the order.

           Args:
               order_id (str): The ID of the order placed.

           Returns:
               dict (str) with keys = locations of ordered images and
               values = status of each ordered image.
        '''

        print 'Get status of order ' + order_id
        url = 'https://geobigdata.io/orders/v2/order/'
        r = self.gbdx_connection.get(url + order_id)
        lines = r.json().get("acquisitions", {})
        results = []
        for line in lines:
            location = line['location']
            status = line["state"]
            results.append((location, status))

        return dict(results)


    def launch_workflow(self, workflow):
        '''Launches GBDX workflow.

           Args:
               workflow (dict): Dictionary specifying workflow tasks.

           Returns:
               Workflow id (str).
        '''

        # hit workflow api
        url = 'https://geobigdata.io/workflows/v1/workflows'
        try:
            r = self.gbdx_connection.post(url, json=workflow)
            workflow_id = r.json()['id']
            return workflow_id
        except TypeError:
            print 'Workflow not launched!'


    def check_workflow_status(self, workflow_id):
        '''Checks workflow status.

         Args:
             workflow_id (str): Workflow id.

         Returns:
             Workflow status (str).
        '''
        print 'Get status of workflow: ' + workflow_id
        url = 'https://geobigdata.io/workflows/v1/workflows/' + workflow_id
        r = self.gbdx_connection.get(url)

        return r.json()['state']


    def get_task_definition(self, task_name):
        '''Get task definition.

         Args:
             task_name (str): The task name.

         Return:
             Task definition (dict).
        '''

        url = 'https://geobigdata.io/workflows/v1/tasks/' + task_name
        r = self.gbdx_connection.get(url)

        return r.json()


    def launch_aop_to_s3_workflow(self,
                                  input_location,
                                  output_location,
                                  bands='Auto',
                                  ortho_epsg='EPSG:4326',
                                  enable_pansharpen='false',
                                  enable_acomp='false',
                                  enable_dra='false',
                                  ):

        '''Launch aop_to_s3 workflow with choice of select parameters. There
           are more parameter choices to this workflow than the ones provided
           by this function. In this case, use the more general
           launch_workflow function.

           Args:
               input_location (str): Imagery location on S3.
               output_location (str): Output imagery S3 location within user prefix.
                                      This should not be preceded with nor followed
                                      by a backslash.
               bands (str): Bands to process (choices are 'Auto', 'MS', 'PAN', default
                            is 'Auto'). If enable_pansharpen = 'true', leave the default
                            setting.
               ortho_epsg (str): Choose projection (default 'EPSG:4326').
               enable_pansharpen (str): Apply pansharpening (default 'false').
               enable_acomp (str): Apply ACOMP (default 'false').
               enable_dra (str): Apply dynamic range adjust (default 'false').
           Returns:
               Workflow id (str).
        '''

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

        aop_to_s3['tasks'][0]['inputs'][0]['value'] = input_location
        aop_to_s3['tasks'][0]['inputs'][1]['value'] = bands
        aop_to_s3['tasks'][0]['inputs'][2]['value'] = enable_acomp
        aop_to_s3['tasks'][0]['inputs'][3]['value'] = enable_dra
        aop_to_s3['tasks'][0]['inputs'][4]['value'] = ortho_epsg
        aop_to_s3['tasks'][0]['inputs'][5]['value'] = enable_pansharpen

        # use the user bucket and prefix information to set output location
        s3_info = self.get_s3_info()
        bucket = s3_info['bucket']
        prefix = s3_info['prefix']
        output_location_final = 's3://' + '/'.join([bucket, prefix, output_location])
        aop_to_s3['tasks'][1]['inputs'][1]['value'] = output_location_final

        # launch workflow
        print 'Launch workflow'
        workflow_id = self.launch_workflow(aop_to_s3)

        return workflow_id

    
    def download_from_s3(self, location, local_dir='.'):
        '''Download content from bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           If location is a directory, all files in the directory are
           downloaded. If it is a file, then that file is downloaded.

           Args:
               location (str): S3 location within prefix. 
               local_dir (str): Local directory where file(s) will be stored.
                                Default is here.
        '''

        print 'Getting S3 info'
        s3_info = self.get_s3_info()
        bucket = s3_info['bucket']
        prefix = s3_info['prefix']
        access_key = s3_info['S3_access_key']
        secret_key = s3_info['S3_secret_key']
        session_token = s3_info['S3_session_token']

        print 'Connecting to S3'
        s3conn = s3.connect_to_region('us-east-1', aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key,
                                      security_token=session_token)

        b = s3conn.get_bucket(bucket, validate=False,
                              headers={'x-amz-security-token': session_token})

        # remove head and/or trail backslash from location
        if location[0] == '/':
            location = location[1:]
        if location[-1] == '/':
            location = location[:-2]    

        whats_in_here = b.list(prefix + '/' + location)

        print 'Downloading contents'
        for key in whats_in_here:
            filename = key.name.split('/')[-1]
            print filename
            res = key.get_contents_to_filename(local_dir + '/' + filename)

        print 'Done!'


    def delete_in_s3(self, location):
        '''Delete content in bucket/prefix/location.
           Location can be a directory or a file (e.g., my_dir or my_dir/my_image.tif)
           If location is a directory, all files in the directory are deleted. 
           If it is a file, then that file is deleted.

           Args:
               location (str): S3 location within prefix. Can be a directory or
                               a file (e.g., my_dir or my_dir/my_image.tif)
        '''

        print 'Getting S3 info'
        s3_info = self.get_s3_info()
        bucket = s3_info['bucket']
        prefix = s3_info['prefix']
        access_key = s3_info['S3_access_key']
        secret_key = s3_info['S3_secret_key']
        session_token = s3_info['S3_session_token']

        print 'Connecting to S3'
        s3conn = s3.connect_to_region('us-east-1', aws_access_key_id=access_key,
                                      aws_secret_access_key=secret_key,
                                      security_token=session_token)

        b = s3conn.get_bucket(bucket, validate=False,
                              headers={'x-amz-security-token': session_token})

        # remove head and/or trail backslash from location
        if location[0] == '/':
            location = location[1:]
        if location[-1] == '/':
            location = location[:-2]

        whats_in_here = b.list(prefix + '/' + location)

        print 'Deleting contents'

        for key in whats_in_here:
            b.delete_key(key)

        print 'Done!'


    def get_strip_footprint_wkt(self, catID):
        '''Retrieves the strip footprint WKT string given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            footprint (str): A POLYGON of coordinates.
        '''

        print 'Retrieving strip footprint'
        url = ('https://geobigdata.io/catalog/v1/record/' 
               + catID + '?includeRelationships=false')

        r = self.gbdx_connection.get(url)
        if r.status_code == 200:
            footprint = r.json()['properties']['footprintWkt']
            return footprint
        elif r.status_code == 404:
            print 'Strip not found: %s' % catID
            r.raise_for_status()
        else:
            print 'There was a problem retrieving catid: %s' % catID
            r.raise_for_status()


    def get_idaho_images_by_catid(self, catid):
        ''' Retrieves the IDAHO image records associated with a given catid.

        Args:
            catid (str): The source catalog ID from the platform catalog.

        Returns:
            results (json): The full catalog-search response for IDAHO images 
                            within the catID.

        '''

        print 'Retrieving IDAHO metadata'

        # get the footprint of the catid's strip
        footprint = self.get_strip_footprint_wkt(catid)
        if not footprint:
            print 'Cannot get IDAHO metadata for strip %s, footprint not found' % catid
            return None

        # use the footprint to get the IDAHO ID
        url = 'https://geobigdata.io/catalog/v1/search'

        body = {"startDate": None,
                "filters": ["vendorDatasetIdentifier3 = '%s'" % catid],
                "endDate": None,
                "types": ["IDAHOImage"],
                "searchAreaWkt": footprint}

        headers = {'Content-Type': 'application/json'}

        r = self.gbdx_connection.post(url, data=json.dumps(body), headers=headers)
        r.raise_for_status()
        if r.status_code == 200:
            results = r.json()
            numresults = len(results['results'])
            print '%s IDAHO images found associated with catid %s' % (numresults, catid)

            return results


    def describe_idaho_images(self, idaho_image_results):
        ''' Describe a set of IDAHO images, as returned in catalog search results.

        Args:
            idaho_image_results (dict): IDAHO image result set as returned from 
                                        the catalog.
        Returns:
            results (json): the full catalog-search response for IDAHO images 
                            within the catID.
        '''

        results = idaho_image_results['results']

        # filter only idaho images:
        results = [r for r in results if r['type']=='IDAHOImage']
        print 'Describing %s IDAHO images.' % len(results)

        # figure out which catids are represented in this set of images
        catids = set([r['properties']['vendorDatasetIdentifier3'] for r in results])

        description = {}

        for catid in catids:
            # images associated with a single catid
            description[catid] = {}
            description[catid]['parts'] = {}
            description[catid]['sensorPlatformName'] = results[0]['properties']['sensorPlatformName']
            images = [r for r in results if r['properties']['vendorDatasetIdentifier3'] == catid]
            for image in images:
                part = int(image['properties']['vendorDatasetIdentifier2'][-3:])
                color = image['properties']['colorInterpretation']
                bucket = image['properties']['imageBucketName']
                id = image['identifier']
                boundstr = image['properties']['imageBoundsWGS84']

                try:
                    description[catid]['parts'][part]
                except:
                    description[catid]['parts'][part] = {}

                description[catid]['parts'][part][color] = {}
                description[catid]['parts'][part][color]['id'] = id
                description[catid]['parts'][part][color]['bucket'] = bucket
                description[catid]['parts'][part][color]['boundstr'] = boundstr

        return description


    def create_idaho_leaflet_viewer(self, idaho_image_results, outputfilename):
        '''Create a leaflet viewer html file for viewing idaho images

        Args:
            idaho_image_results (dict): IDAHO image result set as returned from the catalog.
            outputfilename (str): where to save an output html file
        '''

        description = self.describe_idaho_images(idaho_image_results)
        for catid, images in description.iteritems():
            functionstring = ''
            for partnum, part in images['parts'].iteritems():

                num_images = len(part.keys())
                partname = None
                if num_images == 1:
                    # there is only one image, use the PAN
                    partname = [p for p in part.keys() if p.upper() == 'PAN'][0]
                    pan_image_id = ''
                elif num_images == 2:
                    # there are two images in this part, use the multi (or pansharpen)
                    partname = [p for p in part.keys() if p is not 'PAN'][0]
                    pan_image_id = part['PAN']['id']

                if not partname:
                    print "Cannot find part for idaho image."
                    continue

                bandstr = {
                    'RGBN': '0,1,2',
                    'WORLDVIEW_8_BAND': '4,3,2',
                    'PAN': '0'
                }.get(partname, '0,1,2')

                part_boundstr_wkt = part[partname]['boundstr']
                part_polygon = geometry.from_wkt(part_boundstr_wkt)
                bucketname = part[partname]['bucket']
                image_id = part[partname]['id']
                W, S, E, N = part_polygon.bounds

                functionstring += "addLayerToMap('%s','%s',%s,%s,%s,%s,'%s');\n" % (bucketname, image_id, W,S,E,N, pan_image_id)

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(os.path.realpath('__file__'))))
        with open(os.path.join(__location__, 'leafletmap_template.html'), 'r') as htmlfile:
            data=htmlfile.read().decode("utf8")

        data = data.replace('FUNCTIONSTRING',functionstring)
        data = data.replace('CENTERLAT',str(S))
        data = data.replace('CENTERLON',str(W))
        data = data.replace('BANDS',bandstr)
        data = data.replace('TOKEN',self.gbdx_connection.access_token)

        with codecs.open(outputfilename,'w','utf8') as outputfile:
            print "Saving %s" % outputfilename
            outputfile.write(data)


    def get_idaho_tiles_by_zxy(self, catID, z, x, y, outputFolder):
        '''Retrieves IDAHO tiles of a given catID for a particular z, x, and
           y.  The z, x, and y must be known ahead of time and must intersect
           the strip boundaries of the particular catID to return content.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            Confirmation (str) that tile processing was done.
        '''

        print 'Retrieving IDAHO tiles'

        # get the bucket name and IDAHO ID of each tile within the catID

        locations = self.get_idaho_images_by_catid(catID)
        access_token = self.gbdx_connection.access_token
        for location in locations:
            bucket_name = location[0]['imageBucketName']
            idaho_id = location[1]

            # form request
            url = ('http://idahotms-env.us-west-2.elasticbeanstalk.com/'
                   'v1/tile/' + bucket_name + '/' + idaho_id + '/' + str(z)
                   + '/' + str(x) + '/' + str(y) + '?token=' + access_token)
            body = {"token": access_token}

            r = self.gbdx_connection.get(url, data=json.dumps(body), stream=True)

            # form output path
            file_path = os.path.join(outputFolder, 
                                     catID + '-'.join(map(str, [z, x, y])) + '.tif')

            # save returned image
            i = Image.open(StringIO(r.content))
            saved = i.save(file_path)

        if saved == None:
            return 'Retrieval complete; please check output folder.'
        else:
            return 'There was a problem saving the file at ' + file_path + '.'

    def get_idaho_chip(self, bucket_name, idaho_id, center_lat, center_lon, 
                       pixel_res_meters, output_folder):
        '''Downloads an orthorectified IDAHO chip.

        Args:
            bucket_name (str): The S3 bucket name.
            idaho_id (str): The IDAHO ID of the chip.
            center_lat (str): The latitude of the center of the desired chip.
            center_lon (str): The longitude of the center of the desired chip.
            pixel_res_meters (str): Pixel resolution in meters.
            output_folder (str): The folder the chip should be output to.

        Returns:
            Confirmation (str) that tile processing was done.
        '''

        print 'Retrieving IDAHO chip'
        
        # form request
        url = ('http://idaho.geobigdata.io/'
               'v1/chip/' + bucket_name + '/' + idaho_id + '?lat=' 
               + str(center_lat) + '&long=' + str(center_lon) + '&resolution='
               + str(pixel_res_meters))
       
        r = requests.get(url)

        if r.status_code == 200:
            # form output path
            file_path = output_folder + '/' + idaho_id + '.tif'
    
            # save returned image
            i = Image.open(StringIO(r.content))
            i.save(file_path)
    
        elif r.status_code == 404:
            print 'IDAHO ID not found: %s' % idaho_id
            r.raise_for_status()
        else:
            print 'There was a problem retrieving IDAHO ID: %s' % idaho_id
            r.raise_for_status()

    def view_idaho_tiles_by_bbox(self, catId, bbox, outputfilename):
        '''Retrieve and view just the IDAHO chips in a particular bounding box
           for a catID.

        Args:
            catid (str): The source catalog ID from the platform catalog.
            bbox (list): List of coords: minx(W), miny(S), maxx(E), maxy(N).
            outputfilename (str): a Leaflet Viewer file showing the IDAHO
               images as tiles.
        '''
        
        minx, miny, maxx, maxy = bbox
        
        #validate bbox values
        if (minx > maxx):
            print ('The west value is not less than the east value.')
            exit
        if (miny > maxy):
            print ('The south value is not less than the north value.')
            exit
        
        #create bbox polygon
        bp1 = Point(minx, miny)
        bp2 = Point(minx, maxy)
        bp3 = Point(maxx, maxy)
        bp4 = Point(maxx, miny)
        bbox_polygon = Polygon(bp1, bp2, bp3, bp4)
        
        #get IDAHO image results: parts
        idaho_image_results = self.get_idaho_images_by_catid(catId)
        description = self.describe_idaho_images(idaho_image_results)
        
        tile_count = 0
        for catid, images in description.iteritems():
            functionstring = ''
            for partnum, part in images['parts'].iteritems():

                num_images = len(part.keys())
                partname = None
                if num_images == 1:
                    # there is only one image, use the PAN
                    partname = [p for p in part.keys() if p.upper() == 'PAN'][0]
                    pan_image_id = ''
                elif num_images == 2:
                    # there are two images in this part, use the multi (or pansharpen)
                    partname = [p for p in part.keys() if p is not 'PAN'][0]
                    pan_image_id = part['PAN']['id']

                if not partname:
                    print "Cannot find part for idaho image."
                    continue

                bandstr = {
                    'RGBN': '0,1,2',
                    'WORLDVIEW_8_BAND': '4,3,2',
                    'PAN': '0'
                }.get(partname, '0,1,2')

                part_boundstr_wkt = part[partname]['boundstr']
                part_polygon = geometry.from_wkt(part_boundstr_wkt) 
                bucketname = part[partname]['bucket']
                image_id = part[partname]['id']
                W, S, E, N = part_polygon.bounds
                pp1, pp2, pp3, pp4 = Point(W, S), Point(W, N), Point(E, N), Point(E, S)
                part_bbox_polygon = Polygon(pp1, pp2, pp3, pp4)
                if (bbox_polygon.intersection(part_bbox_polygon)):
                    functionstring += ("addLayerToMap('%s','%s',%s,%s,%s,%s,'%s');\n" % 
                                      (bucketname, image_id, W,S,E,N, pan_image_id))
                    tile_count += 1
                    
        print ('There were ' + str(tile_count) + ' IDAHO images found to ' +
              'intersect with the provided bounding box.')
        
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(os.path.realpath('__file__'))))
        with open(os.path.join(__location__, 'leafletmap_template.html'), 'r') as htmlfile:
            data=htmlfile.read().decode("utf8")

        data = data.replace('FUNCTIONSTRING',functionstring)
        data = data.replace('CENTERLAT',str(S + (N-S)/2))
        data = data.replace('CENTERLON',str(W + (E-W)/2))
        data = data.replace('BANDS',bandstr)
        data = data.replace('TOKEN',self.gbdx_connection.access_token)

        with codecs.open(outputfilename,'w','utf8') as outputfile:
            print "Saving %s" % outputfilename
            outputfile.write(data)
            
    def download_idaho_tiles_by_bbox(self, catId, bbox, resolution, outputfolder):
        '''Retrieve and view just the IDAHO chips in a particular bounding box
           for a catID.

        Args:
            catid (str): The source catalog ID from the platform catalog.
            bbox (list): List of coords: minx(W), miny(S), maxx(E), maxy(N).
            resolution (str): The desired floating point resolution of the tiles.
            outputfolder (str): The desired output location of the IDAHO tiles.
        '''
        
        minx, miny, maxx, maxy = bbox
        
        #validate bbox values
        if (minx > maxx):
            print ('The west value is not less than the east value.')
            exit
        if (miny > maxy):
            print ('The south value is not less than the north value.')
            exit
        
        #create bbox polygon
        bp1 = Point(minx, miny)
        bp2 = Point(minx, maxy)
        bp3 = Point(maxx, maxy)
        bp4 = Point(maxx, miny)
        bbox_polygon = Polygon(bp1, bp2, bp3, bp4)
        
        #get IDAHO image results: parts
        idaho_image_results = self.get_idaho_images_by_catid(catId)
        description = self.describe_idaho_images(idaho_image_results)
        
        tile_count = 0
        for catid, images in description.iteritems():
            for partnum, part in images['parts'].iteritems():

                num_images = len(part.keys())
                partname = None
                if num_images == 1:
                    # there is only one image, use the PAN
                    partname = [p for p in part.keys() if p.upper() == 'PAN'][0]
                elif num_images == 2:
                    # there are two images in this part, use the multi (or pansharpen)
                    partname = [p for p in part.keys() if p is not 'PAN'][0]

                if not partname:
                    print "Cannot find part for idaho image."
                    continue

                part_boundstr_wkt = part[partname]['boundstr']
                part_polygon = geometry.from_wkt(part_boundstr_wkt) 
                bucketname = part[partname]['bucket']
                image_id = part[partname]['id']
                W, S, E, N = part_polygon.bounds
                pp1, pp2, pp3, pp4 = Point(W, S), Point(W, N), Point(E, N), Point(E, S)
                part_bbox_polygon = Polygon(pp1, pp2, pp3, pp4)
                if (bbox_polygon.intersection(part_bbox_polygon)):
                    center_lat = (S + (N-S)/2)
                    center_lon = (W + (E-W)/2)
                    print center_lat, center_lon
                    self.get_idaho_chip(bucketname, image_id, center_lat, 
                                        center_lon, resolution, outputfolder)
                    tile_count+=1
                    
        print ('There were ' + str(tile_count) + ' IDAHO images downloaded that ' +
              'intersect with the provided bounding box.')
        
       