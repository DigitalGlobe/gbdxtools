'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com

GBDX IDAHO Interface
'''

from StringIO import StringIO
from PIL import Image
from pygeoif import geometry
import codecs

from gbdxtools.catalog import Catalog

class Idaho():

    def __init__(self, connection):
        ''' Construct the Idaho interface class
            Args:
                connection: a ref to the GBDX Connection

            Returns:
                an instance of the Idaho interface class

        '''
        self.gbdx_connection = connection
        self.catalog = Catalog(self.gbdx_connection)


    def get_images_by_catid(self, catid):
        ''' Retrieves the IDAHO image records associated with a given catid.

        Args:
            catid (str): The source catalog ID from the platform catalog.

        Returns:
            results (json): The full catalog-search response for IDAHO images 
                            within the catID.

        '''

        print 'Retrieving IDAHO metadata'

        # get the footprint of the catid's strip
        footprint = self.catalog.get_strip_footprint_wkt(catid)
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

    def describe_images(self, idaho_image_results):
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

    def get_tiles_by_zxy(self, catID, z, x, y, outputFolder):
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
        locations = self.get_tile_locations(catID)
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
            r.raise_for_status()

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

    def create_leaflet_viewer(self, idaho_image_results, outputfilename):
        '''Create a leaflet viewer html file for viewing idaho images

        Args:
            idaho_image_results (dict): IDAHO image result set as returned from the catalog.
            outputfilename (str): where to save an output html file
        '''

        description = self.describe_images(idaho_image_results)
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
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
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
