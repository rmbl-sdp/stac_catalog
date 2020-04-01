import pystac as stac
import os
import rasterio
from shapely.geometry import Polygon, mapping

catalog_dir = "/home/rstudio/IanBreckheimer/SDP_S3_Uploads/draft_products/"
web_dir = "https://rmbl-sdp.s3.amazonaws.com/data_products/draft/"

catalog = stac.catalog(id='sdp-catalog', 
                       description='Catalog for SDP Data Products')

path1 = os.path.join(web_dir,"UER_canopy_ht_1m_v1.tif")
metapath1 = os.path.join(web_dir,"UER_canopy_ht_1m_v1_metadata.xml")
thumbpath1 = os.path.join(web_dir,"UER_canopy_ht_1m_v1_thumbnail.png")
path2 =  os.path.join(web_dir,"UER_landcover_1m_v1.tif")
metapath2 = os.path.join(web_dir,"UER_landcover_1m_v1_metadata.xml")
thumbpath2 = os.path.join(web_dir,"UER_landcover_1m_v1_thumbnail.png")

def get_bbox_and_footprint(raster_uri):
    with rasterio.open(raster_uri) as ds:
        bounds = ds.bounds
        bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
        footprint = Polygon([
            [bounds.left, bounds.bottom],
            [bounds.left, bounds.top],
            [bounds.right, bounds.top],
            [bounds.right, bounds.bottom]
        ])
        
        return (bbox, mapping(footprint))
        
bbox1, footprint1 = get_bbox_and_footprint(path1)
bbox2, footprint2 = get_bbox_and_footprint(path2)

from datetime import datetime

item1 = stac.Item(id='canopy-height',
                 geometry=footprint1,
                 bbox=bbox1,
                 datetime=datetime(2018,7,5),
                 properties={})
                 
item2 = stac.Item(id='landcover',
                 geometry=footprint2,
                 bbox=bbox2,
                 datetime=datetime(2019,7,5),
                 properties={})
                 
item1.add_asset(key='data', asset=stac.Asset(href=path1, media_type=stac.MediaType.COG))
item1.add_asset(key='metadata',asset=stac.Asset(href=metapath1,media_type=stac.MediaType.XML))
item1.add_asset(key='thumbnail',asset=stac.Asset(href=thumbpath1,media_type=stac.MediaType.PNG))
item2.add_asset(key='data', asset=stac.Asset(href=path2, media_type=stac.MediaType.COG))
item2.add_asset(key='metadata',asset=stac.Asset(href=metapath1,media_type=stac.MediaType.XML))
item2.add_asset(key='thumbnail',asset=stac.Asset(href=thumbpath2,media_type=stac.MediaType.PNG))

## Temporal and Spatial Extent
collection_interval = sorted([item1.datetime, item2.datetime])
temporal_extent = stac.TemporalExtent(intervals=[collection_interval])
spatial_extent = stac.SpatialExtent(bboxes=[bbox1,bbox2])
collection_extent = stac.Extent(spatial=spatial_extent, temporal=temporal_extent)

collection = stac.Collection(id='static-maps', 
                             description='Collection of Static GIS Maps',
                             extent=collection_extent,
                             license='CC-BY-SA-4.0')


collection.add_items([item1,item2])


catalog.add_child(collection)


catalog.describe()

catalog.normalize_hrefs(os.path.join(catalog_dir, 'stac'))
catalog.save(catalog_type=stac.CatalogType.RELATIVE_PUBLISHED)

##Replace local path in catalog.json with web path and upload to s3.

os.system("/usr/local/bin/aws2 s3 sync /home/rstudio/IanBreckheimer/SDP_S3_Uploads/draft_products/ s3://rmbl-sdp/data_products/draft/ --acl 'public-read'")
