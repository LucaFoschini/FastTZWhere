FastTZWhere
===========

Offline, fast, daylight-saving-aware timezone lookup from world-wide lat/long.

Answer the question "What was the local time in Bologna exactly 3 years ago?"

Put another way, computes the (Daylight Saving-aware) timezone from a
lat/long geolocation.

It doesn't require an internet connection (except for the first time
your run it, when the Olson Database needs to be downloaded)

Inspired by:
[pytzwhere](https://github.com/pegler/pytzwhere/blob/master/tzwhere/tzwhere.py),
with the following improvements:

- Daylight Saving Time is taken into consideration (through pytz)
- Reverse geolocation is very fast (based on RTree and
  [libspatialindex](https://github.com/libspatialindex/libspatialindex))
- Uses [Fiona](https://pypi.python.org/pypi/Fiona)/[Shapely](https://pypi.python.org/pypi/Shapely)(Python GIS) to deal with shapefiles.
- Batteries included. The class initialization takes care of
  retrieving the necessary external information

Installation
========

 * Install [libspatialindex](https://github.com/libspatialindex/libspatialindex)). On a mac:

   	   wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.1.tar.gz
	   tar -xzvf spatialindex-src-1.8.1.tar.gz 
	   cd spatialindex-src-1.8.1
	   ./configure; make; make install

 * Install the rest of the requirements:

   	   pip install -r requirements.txt

Run
======

	python FastTZWhere.py

 * The first time you'll see


       Downloading the TZ shapefile (Olson database)...
       Done.
       Building the spatial index on the shapefile...
       Done.
       UTC+0200
       UTC+0100

 * All the other times:

       Loading Rtree and Pickle File
       UTC+0200
       UTC+0100
