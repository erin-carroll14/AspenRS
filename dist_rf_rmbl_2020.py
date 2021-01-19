# connect to google drive
from google.colab import drive
drive.mount('/content/drive')

# import earth engine library
import ee
import folium
from folium import plugins

# establish connection to own earth engine account
ee.Authenticate()
ee.Initialize()

# Commented out IPython magic to ensure Python compatibility.
# call 2019 imagery stack
# %cd /content/drive/My\ Drive/Colab\ Notebooks/Aspen/Cytotype

from S2SRstack2020 import stacked2020_JunOct, Colorado

# Veg mask
col = ee.ImageCollection('COPERNICUS/S2_SR').filterBounds(Colorado).filterDate('2020-01-01', '2021-01-01')

# function to get only pixels classified as veg at any point in year
def getVeg(img):
  return img.mask(img.select('SCL').eq(4))

colVeg = col.map(getVeg)
imgVeg = colVeg.qualityMosaic('SCL')

# mask stacked imagery by 2020 veg mask
stackVeg = stacked2020_JunOct.mask(imgVeg.select('SCL'))

# clip to RMBL
RMBL = ee.Geometry.Polygon([[-107.22694538043767,38.75434750566651],
                            [-106.74629352496892,38.75434750566651],
                            [-106.74629352496892,39.08236920480586],
                            [-107.22694538043767,39.08236920480586],
                            [-107.22694538043767,38.75434750566651]])

stackVegRMBL2020 = stackVeg.clip(RMBL)

# prepare reference data

# load aspen reference points
aspen = ee.FeatureCollection('users/erin_carroll/aspenAssets/refAspen')

# add 'class' field (1=aspen presence)
def getClass1(f):
  return f.set('class', 1)
aspen = aspen.map(getClass1)

# load non-aspen reference points
nonAspen = ee.FeatureCollection('users/erin_carroll/aspenAssets/refNonAspen')

# add 'class' field (0=absence)
def getClass0(f):
  return f.set('class', 0)
nonAspen = nonAspen.map(getClass0)

# merge aspen and non-aspen points
ref = aspen.merge(nonAspen)

# prepare training data from reference data

# extract image bands at reference points, keep 'class' property from reference points
reference = stackVegRMBL2020.sampleRegions(**{
  'collection': ref,
  'properties': ['class'],
  'scale': 10
})

# subset validation sample (25%)
random = reference.randomColumn('x')
validation = random.filter(ee.Filter.lt('x', 0.25))
training = random.filter(ee.Filter.gte('x', 0.25))

# create and train model
bandsAll = ['B2', 'B2_1', 'B2_2', 'B2_3', 'B2_4', 'B3', 'B3_1', 'B3_2', 'B3_3', 'B3_4', 'B4', 'B4_1', 'B4_2', 'B4_3', 'B4_4', 'B5', 'B5_1', 'B5_2', 'B5_3', 'B5_4', 'B6', 'B6_1', 'B6_2', 'B6_3', 'B6_4', 'B7', 'B7_1', 'B7_2', 'B7_3', 'B7_4', 'B8', 'B8_1', 'B8_2', 'B8_3', 'B8_4', 'B8A', 'B8A_1', 'B8A_2', 'B8A_3', 'B8A_4', 'B11', 'B11_1', 'B11_2', 'B11_3','B11_4', 'B12', 'B12_1', 'B12_2', 'B12_3', 'B12_4']

classifier = ee.Classifier.smileRandomForest(10).train(**{
      'features': training,
      'classProperty': 'class',
      'inputProperties': bandsAll
    });

# deploy model
aspenMask2020 = stackVegRMBL2020.classify(classifier)