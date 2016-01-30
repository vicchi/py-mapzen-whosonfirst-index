# https://pythonhosted.org/setuptools/setuptools.html#namespace-packages
__import__('pkg_resources').declare_namespace(__name__)

import logging
import shapely.geometry

import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export
import mapzen.whosonfirst.pip.utils
import mapzen.whosonfirst.mapshaper.utils

class geojson(mapzen.whosonfirst.export.flatfile):

    def __init__(self, root, **kwargs):

        self.root = root

        # TO DO: pip-server args

        self.mapshaper = kwargs.get('mapshaper', False)

        mapzen.whosonfirst.export.flatfile.__init__(self, root, **kwargs)

    def index_feature(self, feature, **kwargs):

        # MAYBE: move all of this in to a separate function or make it
        # part of py-mapzen-whosonfirst-validator (20160129/thisisaaronland)

        # MAYBE: use some derivation of https://github.com/whosonfirst/whosonfirst-json-schema
        # https://github.com/whosonfirst/whosonfirst-json-schema

        geom = feature.get('geometry', None)

        if not geom:
            raise Exception, "Missing geometry"

        try:
            shapely.geometry.asShape(geom)
        except Exception, e:
            raise Exception, "Invalid geometry (%s)" % e

        props = feature.get('properties', None)

        if not props:
            raise Exception, "Missing properties"
        
        required = (
            'wof:name',
            'wof:placetype',
            'wof:country'
        )

        for what in required:

            if not props.get(what, None):
                raise Exception, "Missing required field %s" % what
                
        if not props.get('iso:country', None):
            props['iso:country'] = props['wof:country']
        
        if not mapzen.whosonfirst.placetypes.is_valid_placetype(props['wof:placetype']):
            raise Exception, "Invalid placetype"

        # MAYBE: do wof:id minting here (rather than in py-mz-wof-export)
        # (20160129/thisisaaronland)

        # TODO: pip-server flags 

        mapzen.whosonfirst.pip.utils.append_hierarchy_and_parent_pip(feature, data_root=[self.root])

        if self.mapshaper:
            mapzen.whosonfirst.mapshaper.utils.append_mapshaper_centroid(feature, mapshaper=self.mapshaper)
        
        path = self.export_feature(feature, **kwargs)
        return path
