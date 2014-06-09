#!/usr/bin/python

import fiona
import urllib
from shapely.geometry import shape
from shapely import speedups
import shapely

from rtree import index

import pickle
import os
import os.path
import operator 
import sys

from datetime import datetime, timedelta
from pytz import timezone
import pytz

class FastTZWhere():

    def __init__(self, force_recompute = False):
        """Initialize the local data files.
        
        The first time it will:
        - Create a directory named "datadir" in this file's current directory
        - Download the Olson database and place it in ./datadir
        - Create an Rtree on the shapes in the database and persist it in ./datadir
        - Create an additional bookmarking dict() and persist (via pickle) it in ./datadir 

        All the other times it will:
        - Load the RTree and the additional bookmarking dict() in memory
        
        Keyword arguments:
        force_recompute -- if True, deletes and recomputes the local data
        """

        data_dir =  "%s/datadir" % os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
            
        data_files = ['rtree.dat', 'rtree.idx', 'rtree.p']

        # at least one file is missing
        if  force_recompute or (not reduce(operator.and_, [os.path.isfile("%s/%s" % (data_dir,x)) for x in data_files])):

            tz_fname = "%s/%s" % (data_dir, 'tz_world.zip')
            print >> sys.stderr, "Downloading the TZ shapefile (Olson database)..."
            urllib.urlretrieve ('http://efele.net/maps/tz/world/tz_world.zip', tz_fname)
            print >> sys.stderr, "Done."

            for x in data_files:
                if  os.path.isfile("%s/%s" % (data_dir,x)): 
                    os.remove("%s/%s" % (data_dir,x))

            self.idx = index.Rtree('%s/rtree' % data_dir)
            with fiona.drivers():
                print >> sys.stderr, "Building the spatial index on the shapefile..."
                with fiona.open('/world/tz_world.shp',
                                vfs='zip://%s' % tz_fname) as collection:
                    self.polyd = {}
                    i = 0
                    for polygon in collection:
                        p = shape(polygon['geometry'])
                        self.idx.add(i,shape(p).bounds)
                        self.polyd[i] = {'shape' : p, 'tzid': polygon['properties']['TZID']}
                        i += 1
                with open('%s/rtree.p' % data_dir, 'w') as f:
                    pickle.dump(self.polyd, f)

                print >> sys.stderr, "Done."

        else:
            print >> sys.stderr, "Loading Rtree and Pickle File"
            self.idx = index.Rtree('%s/rtree' % data_dir)
            with open('%s/rtree.p' % data_dir) as f:
                self.polyd = pickle.load(f)

    def get_timezone(self, latitude, longitude):
        """Returns the timezone of a geolocation expressed in lat/long.
        
        Looks up the lat/long in the Rtree.

        Keyword arguments:
        latitude/longitude -- the coordinate to be looked up.

        Returns:
        A pytz.timezone object
        """

        point = shapely.geometry.Point(longitude, latitude) # longitude, latitude
            
        hits = list(self.idx.intersection((point.x,point.y,point.x,point.y)))

        tzs = [self.polyd[i]['tzid'] for i in hits if self.polyd[i]['shape'].intersection(point)]
        if tzs:
            return timezone(tzs[0])
        else:
            return None
       
    def timeAt(self, latitude, longitude, utc_dt):
        """Returns the local time at a specific lat/long  and time, formatted as as string. 
        
        Takes into account Daylight Saving Time.

        Keyword arguments:
        latitude/longitude -- the coordinate to be looked up.
        utc_dt -- a UTC datetime
        """

        tz = self.get_timezone(latitude, longitude)
        if tz:
            return tz.normalize(utc_dt)
        else:
            print "Location Not Found"
            return None

    def formattedTimeAt(self, latitude, longitude, utc_dt = datetime(*datetime.now().timetuple()[0:7], tzinfo=pytz.utc)):
        """Convert the output of timeAt into a ISO 8601 time representation string"""

        t = self.timeAt(latitude,longitude, utc_dt)
        if t:
            return t.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        return ''
    
    def tzAt(self, latitude, longitude, utc_dt = datetime(*datetime.now().timetuple()[0:7], tzinfo=pytz.utc)):
        """Convert the output of timeAt retaining the timezone information only"""

        t = self.timeAt(latitude,longitude, utc_dt)
        if t:
            return t.strftime('UTC%z')
        return ''
            

if __name__ == "__main__":

    w  = FastTZWhere()
    # Bologna
    latitude = 44.4991182 
    longitude = 11.3316855 
    
    # Daylight Saving Time in effect
    print w.tzAt(latitude, longitude, datetime(2002, 7, 27, 6, 0, 0, tzinfo=pytz.utc))

    # Standard Time in effect
    print w.tzAt(latitude, longitude, datetime(2002, 12, 27, 6, 0, 0, tzinfo=pytz.utc))


