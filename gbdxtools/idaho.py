"""
GBDX IDAHO Interface.

Contact: nate.ricklin@digitalglobe.com
"""

from pygeoif import geometry
from sympy.geometry import Point, Polygon
import codecs
import json
import os
import requests

from gbdxtools.catalog import Catalog

class Idaho():


    def __init__(self, interface):
        ''' Construct the Idaho interface class

        Args:
            connection (gbdx_session): A reference to the GBDX Connection.

        Returns:
            An instance of the Idaho interface class.

        '''
        self.gbdx_connection = interface.gbdx_connection
        self.catalog = Catalog(interface)
        self.logger = interface.logger


    def get_images_by_catid(self, catid):
        ''' Retrieves the IDAHO image records associated with a given catid.

        Args:
            catid (str): The source catalog ID from the platform catalog.

        Returns:
            results (json): The full catalog-search response for IDAHO images
                            within the catID.

        '''

        self.logger.debug('Retrieving IDAHO metadata')

        # get the footprint of the catid's strip
        footprint = self.catalog.get_strip_footprint_wkt(catid)
        if not footprint:
            self.logger.debug('''Cannot get IDAHO metadata for strip %s,
                                 footprint not found''' % catid)
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
            self.logger.debug('%s IDAHO images found associated with catid %s'
                              % (numresults, catid))

            return results


    def describe_images(self, idaho_image_results):
        ''' Describe a set of IDAHO images, as returned in catalog search results.

        Args:
            idaho_image_results (dict): IDAHO image result set as returned from
                                        the catalog.
        Returns:
            results (json): The full catalog-search response for IDAHO images
                            within the catID.
        '''

        results = idaho_image_results['results']

        # filter only idaho images:
        results = [r for r in results if r['type']=='IDAHOImage']
        self.logger.debug('Describing %s IDAHO images.' % len(results))

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


    def create_leaflet_viewer(self, idaho_image_results, output_filename):
        '''Create a leaflet viewer html file for viewing idaho images

        Args:
            idaho_image_results (dict): IDAHO image result set as returned from
                                        the catalog.
            output_filename (str): where to save an output html file
        '''

        description = self.describe_images(idaho_image_results)
        if len(description) > 0:
            functionstring = ''
            for catid, images in description.iteritems():
                for partnum, part in images['parts'].iteritems():

                    num_images = len(part.keys())
                    partname = None
                    if num_images == 1:
                        # there is only one image, use the PAN
                        partname = [p for p in part.keys()][0]
                        pan_image_id = ''
                    elif num_images == 2:
                        # there are two images in this part, use the multi (or pansharpen)
                        partname = [p for p in part.keys() if p is not 'PAN'][0]
                        pan_image_id = part['PAN']['id']

                    if not partname:
                        self.logger.debug("Cannot find part for idaho image.")
                        continue

                    bandstr = {
                        'RGBN': '0,1,2',
                        'WORLDVIEW_8_BAND': '4,2,1',
                        'PAN': '0'
                    }.get(partname, '0,1,2')

                    part_boundstr_wkt = part[partname]['boundstr']
                    part_polygon = geometry.from_wkt(part_boundstr_wkt)
                    bucketname = part[partname]['bucket']
                    image_id = part[partname]['id']
                    W, S, E, N = part_polygon.bounds

                    functionstring += "addLayerToMap('%s','%s',%s,%s,%s,%s,'%s');\n" % (bucketname, image_id, W,S,E,N, pan_image_id)

            __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
            with open(os.path.join(__location__, 'leafletmap_template.html'), 'r') as htmlfile:
                data=htmlfile.read().decode("utf8")

            data = data.replace('FUNCTIONSTRING',functionstring)
            data = data.replace('CENTERLAT',str(S))
            data = data.replace('CENTERLON',str(W))
            data = data.replace('BANDS',bandstr)
            data = data.replace('TOKEN',self.gbdx_connection.access_token)

            with codecs.open(output_filename,'w','utf8') as outputfile:
                self.logger.debug("Saving %s" % output_filename)
                outputfile.write(data)
        else:
            print "No items returned."


    def get_idaho_chip(self, bucket_name, idaho_id, center_lat, center_lon,
                       output_folder, resolution=None, pan_id=None):
        '''Downloads an orthorectified IDAHO chip.

        Args:
            bucket_name (str): The S3 bucket name.
            idaho_id (str): The IDAHO ID of the chip.
            center_lat (str): The latitude of the center of the desired chip.
            center_lon (str): The longitude of the center of the desired chip.
            output_folder (str): The folder the chip should be output to.
            resolution (str): output resolution in meters (default None = native resolution)
            pan_id (str): The associated PAN ID for pan sharpening a multispectral image
        Returns:
            Confirmation (str) that tile processing was done.
        '''

        print 'Retrieving IDAHO chip'

        access_token = self.gbdx_connection.access_token

        # form request
        url = ('http://idaho.geobigdata.io/'
               'v1/chip/centroid/' + bucket_name + '/' + idaho_id + '?lat='
               + str(center_lat) + '&long=' + str(center_lon) +
               '&format=tif' + '&token='+access_token)

        if pan_id:
            url += '&panId=' + pan_id

        if resolution:
            url += '&resolution=' + str(resolution)

        r = requests.get(url)

        if r.status_code == 200:
            # form output path
            file_path = os.path.join(output_folder, idaho_id+'.tif')

            with open(file_path, 'wb') as the_file:
                the_file.write(r.content)

        elif r.status_code == 404:
            print 'IDAHO ID not found: %s' % idaho_id
            r.raise_for_status()
        else:
            print 'There was a problem retrieving IDAHO ID: %s' % idaho_id
            r.raise_for_status()

    def get_idaho_chip_by_bbox(self, idaho_id, output_folder, minx, miny, maxx, maxy,
                               filename=None, bucket_name='idaho-images',
                               high_cutoff = 0.99, low_cutoff = 0.01, pan_id=None,
                               format='tif', return_fp=False):

        '''Downloads an orthorectified IDAHO chip by bounding box.

        Args:
            idaho_id (str): The IDAHO ID of the chip
            output_folder (str): folder in which to save output image
            minx (float): smallest x-value for bounding box corner
            miny (float): smallest y-value for bounding box corner
            maxx (float): largest x-value for bounding box corner
            maxy (float): largest y-value for bounding box corner
            filename (str): optional- name under which to save the chip
            bucket_name (str): The S3 bucket name.
            high_cutoff (float): high threshold cutoff for the DRA opertaion
            low_cutoff (float): low threshold cutoff for the DRA opertaion
            pan_id (str): The associated PAN ID for pan sharpening a multispectral image
            return_fp (bool): return name of the chip file

        Returns:
            Confirmation (str) that tile processing was done.
        '''

        print 'Retrieving IDAHO chip'

        access_token = self.gbdx_connection.access_token

        if not filename:
            filename = idaho_id

        # form request
        url = ('http://idaho.geobigdata.io/'
               'v1/chip/bbox/' + bucket_name + '/' + idaho_id + '?upperLeft='
               + str(minx) + ',' + str(maxy) + '&lowerRight=' + str(maxx) + ','
               + str(miny) + '&lowCutoff=' + str(low_cutoff) + '&highCutoff=' +
               str(high_cutoff) + '&format=' + str(format) + '&token=' + access_token)

        if pan_id:
            url += '&panId='+ pan_id

        r = requests.get(url)

        if r.status_code == 200:
            # form output path
            file_path = os.path.join(output_folder, filename+'.tif')

            with open(file_path, 'wb') as the_file:
                the_file.write(r.content)

                if return_fp:
                    return file_path

        elif r.status_code == 404:
            print 'IDAHO ID not found: %s' % idaho_id
            r.raise_for_status()
        else:
            print 'There was a problem retrieving IDAHO ID: %s' % idaho_id
            r.raise_for_status()

    def view_idaho_tiles_by_bbox(self, catId, bbox, output_filename):
        '''Retrieve and view just the IDAHO chips in a particular bounding box
           for a catID.

        Args:
            catid (str): The source catalog ID from the platform catalog.
            bbox (list): List of coords: minx(W), miny(S), maxx(E), maxy(N).
            output_filename (str): a Leaflet Viewer file showing the IDAHO
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
        idaho_image_results = self.get_images_by_catid(catId)
        description = self.describe_images(idaho_image_results)

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
                    'WORLDVIEW_8_BAND': '4,2,1',
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

        with codecs.open(output_filename,'w','utf8') as outputfile:
            print "Saving %s" % output_filename
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
        idaho_image_results = self.get_images_by_catid(catId)
        description = self.describe_images(idaho_image_results)

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
<<<<<<< HEAD
                    self.get_idaho_chip(bucketname, image_id, center_lat,
                                        center_lon, resolution, outputfolder)
=======
                    self.get_idaho_chip(bucket_name=bucketname,
                                        idaho_id=image_id,
                                        center_lat=str(center_lat),
                                        center_lon=str(center_lon),
                                        resolution=resolution,
                                        output_folder=outputfolder)
>>>>>>> 8e5f8eb73d309df9209e8e558b3eb842ed05b9ec
                    tile_count+=1

        print ('There were ' + str(tile_count) + ' IDAHO images downloaded that ' +
              'intersect with the provided bounding box.')
