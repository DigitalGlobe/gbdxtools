#!/usr/bin/python

#############################################################################################
#
#  get_idaho_chip_gbdxtools_v2.py
#
#  Created by: Dave Loomis
#              Digitalglobe GBD Solutions
#
#  Version 0.1: Dec 15, 2016
#               - example of how to get idaho tif chip
#
#  Usage: python get_idaho_chip_gbdxtools_v2.py
#
#  This script will take an input list of catids and center points
#   and create image chips.  The west, south, east and north coordinates
#   are calculated from the center point and those are fed into the chip
#   service with the catid.
#
#############################################################################################

# use gbdxtools to get the access token
from gbdxtools import Interface 
gbdx = Interface()
token = gbdx.gbdx_connection.access_token

# set the file path
file_path = "/Users/YOUR_USER_NAME/chips/"

# set the list of catids with their centerpoints
catids = [
			[-3.7064,40.4201,'10300100532CAA00'],
			[-3.6472,40.3955,'1030010055B2DB00'],
			[-3.6955,40.3697,'103001005835EB00'],
		 ]

# loop through the list
for c in catids :
	# create the coordinate list list (west,south,east,north)
	coords = [c[0] - 0.001,c[1] - 0.001,c[0] + 0.001,c[1] + 0.001]
	# uncomment to output metadata from the image parts
	##images = gbdx.idaho.get_images_by_catid(c)
	##for k,v in images.iteritems():
	##	print(r['properties'])
	##	print

	# create the chip and save to local drive
	print("saving chip " + c[2] + "_chip.tif" + "...")
	chip = gbdx.idaho.get_chip(coords, c[2], chip_type='PS', chip_format='TIF', filename=file_path + c[2] + '_chip.tif')
