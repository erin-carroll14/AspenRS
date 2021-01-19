# import earth engine library
import ee

# establish connection to own earth engine account
ee.Authenticate()
ee.Initialize()

# define Colorado geometry
Colorado = ee.FeatureCollection('TIGER/2018/States').filter(ee.Filter.eq('STATEFP', '08'))

# define cloud shadow ID parameters
AOI = Colorado
CLD_PRB_THRESH = 10 # cloud probability threshold (0-100). anything greater than the threshold will be considered 'cloud'
NIR_DRK_THRESH = 0.15 # NIR darkness threshold (0-1). pixels with NIR reflectance lower than the threshold will be labeled 'dark'
CLD_PRJ_DIST = 2 # cloud projection distance

# define dates
May = '2020-05-01'
Jun = '2020-06-01'
Jul = '2020-07-01'
Aug = '2020-08-01'
Sep = '2020-09-01'
Oct = '2020-10-01'
Nov = '2020-11-01'

# define functions

# define function to join s2 level-2a imagery and s2cloudless dataset
def joinS2(aoi, start_date, end_date):
    # import and filter s2sr
    s2sr = (ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Import and filter s2cloudless.
    s2srcloudless = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    s2joined = (ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
        'primary': s2sr,
        'secondary': s2srcloudless,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })})))
    
    return s2joined

# define cloud mask function
def add_cloud_bands(img):
  # get s2coudless image, select probability band
  cld_prb = ee.Image(img.get('s2cloudless')).select('probability').rename('cloud_probability')
  # threshold cloud probability for cloud presence/absence  using chosen CLD_PRB_THRESH
  is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')
  # add cloud probability and cloud p/a as image bands
  out = img.addBands(ee.Image([cld_prb, is_cloud]))
  return out

# define shdow mask function
def add_shadow_bands(img):
  # identify water pixels from the SCL band
  not_water = img.select('SCL').neq(6)
  # identify dark NIR pixels that are not water (potential cloud shadow pixels)
  SR_BAND_SCALE = 1e4
  dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')
  # determine the direction to project cloud shadow from clouds (assumes UTM projection)
  shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')))
  # project shadows from clouds for the distance specified by the CLD_PRJ_DIST input
  cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))
  # identify the intersection of dark pixels with cloud shadow projection
  shadows = cld_proj.multiply(dark_pixels).rename('shadows')
  # add dark pixels, cloud projection, and identified shadows as image bands
  out2 = img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))
  return out2

# define final cloud shadow mask
def add_cld_shdw_mask(img):
  # add cloud component bands
  img_cloud = add_cloud_bands(img)
  # add cloud shadow component bands
  img_cloud_shadow = add_shadow_bands(img_cloud)
  # combine cloud and shadow mask, set cloud and shadow as value 1, else 0
  is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0).rename('cloudshadow_mask')
  # add final cloud-shadow mask
  out3 = img_cloud_shadow.addBands(is_cld_shdw)
  return out3

# add band that is inverse of cloudshadow mask (i.e. 0=clouds&shadows, 1=clear)
def getCloudless(img):
  layer = img.select('cloudshadow_mask')
  transformed = layer.subtract(1).multiply(-1).rename('Cloudless')
  return img.addBands(transformed)

# add NDVI band
def getNDVI(img):
  ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
  return img.addBands(ndvi)

# combine Cloudless + NDVI bands
def getCloudShadowNDVI(img):
  combined = img.select('Cloudless').add(img.select('NDVI')).rename('cloudNDVI')
  return img.addBands(combined)

# function to mask land cover types
def getMask(img):
  mask1 = img.select('SCL').gte(4)
  mask2 = img.select('SCL').lte(7)
  mask3 = img.select('SCL').neq(6)
  mask = mask1.multiply(mask2).multiply(mask3)
  return img.mask(mask)

# function to subset bands
bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
def getBands(img):
  return img.select(bands)

# function of functions
def getMonth(start_date, end_date):
  s2joined = (ee.ImageCollection(joinS2(AOI, start_date, end_date)))
  s2masked = s2joined.map(add_cld_shdw_mask)
  s2Cloudless = s2masked.map(getCloudless)
  allBands = s2Cloudless.map(getNDVI)
  cloudNDVI = allBands.map(getCloudShadowNDVI)
  mosaic = cloudNDVI.qualityMosaic('cloudNDVI')
  mosaicMasked = getMask(mosaic)
  return getBands(mosaicMasked)

# get months
mosaic5 = getMonth(May, Jun)
mosaic6 = getMonth(Jun, Jul)
mosaic7 = getMonth(Jul, Aug)
mosaic8 = getMonth(Aug, Sep)
mosaic9 = getMonth(Sep, Oct)
mosaic10 = getMonth(Oct, Nov)
stacked2020_MayOct = mosaic5.addBands(mosaic6).addBands(mosaic7).addBands(mosaic8).addBands(mosaic9).addBands(mosaic10)
stacked2020_JunOct = mosaic6.addBands(mosaic7).addBands(mosaic8).addBands(mosaic9).addBands(mosaic10)

print('stacked2020 loaded')