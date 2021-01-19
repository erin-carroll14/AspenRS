# import earth engine library
import ee

# establish connection to own earth engine account
ee.Authenticate()
ee.Initialize()

# define parameters
bandsAll = ['B2', 'B2_1', 'B2_2', 'B2_3', 'B2_4', 'B3', 'B3_1', 'B3_2', 'B3_3', 'B3_4', 'B4', 'B4_1', 'B4_2', 'B4_3', 'B4_4', 'B5', 'B5_1', 'B5_2', 'B5_3', 'B5_4', 'B6', 'B6_1', 'B6_2', 'B6_3', 'B6_4', 'B7', 'B7_1', 'B7_2', 'B7_3', 'B7_4', 'B8', 'B8_1', 'B8_2', 'B8_3', 'B8_4', 'B8A', 'B8A_1', 'B8A_2', 'B8A_3', 'B8A_4', 'B11', 'B11_1', 'B11_2', 'B11_3','B11_4', 'B12', 'B12_1', 'B12_2', 'B12_3', 'B12_4']

# build function to combine diploid and triploid training samples, train model, deploy
def deploy(train2, train3, trainImage, deployImage):
  trainingC = train2.merge(train3);
  trained = trainImage.sampleRegions(collection=trainingC, properties=['ploidy'], scale=10)
  classifier = ee.Classifier.smileRandomForest(10).train(features=trained, classProperty='ploidy', inputProperties=bandsAll)
  return deployImage.classify(classifier)

def RFmodelPloidy(train2, train3, trainImage, deployImage):
  # build training datasets
  training3_1 = train3.randomColumn('x',1).filter(ee.Filter.lt('x', 0.20))
  training3_2 = train3.randomColumn('x',2).filter(ee.Filter.lt('x', 0.20))
  training3_3 = train3.randomColumn('x',3).filter(ee.Filter.lt('x', 0.20))
  training3_4 = train3.randomColumn('x',4).filter(ee.Filter.lt('x', 0.20))
  training3_5 = train3.randomColumn('x',5).filter(ee.Filter.lt('x', 0.20))
  training3_6 = train3.randomColumn('x',6).filter(ee.Filter.lt('x', 0.20))
  training3_7 = train3.randomColumn('x',7).filter(ee.Filter.lt('x', 0.20))
  training3_8 = train3.randomColumn('x',8).filter(ee.Filter.lt('x', 0.20))
  training3_9 = train3.randomColumn('x',9).filter(ee.Filter.lt('x', 0.20))
  training3_10 = train3.randomColumn('x',10).filter(ee.Filter.lt('x', 0.20))
  training3_11 = train3.randomColumn('x',11).filter(ee.Filter.lt('x', 0.20))
  training3_12 = train3.randomColumn('x',12).filter(ee.Filter.lt('x', 0.20))
  training3_13 = train3.randomColumn('x',13).filter(ee.Filter.lt('x', 0.20))
  training3_14 = train3.randomColumn('x',14).filter(ee.Filter.lt('x', 0.20))
  training3_15 = train3.randomColumn('x',15).filter(ee.Filter.lt('x', 0.20))
  training3_16 = train3.randomColumn('x',16).filter(ee.Filter.lt('x', 0.20))
  training3_17 = train3.randomColumn('x',17).filter(ee.Filter.lt('x', 0.20))
  training3_18 = train3.randomColumn('x',18).filter(ee.Filter.lt('x', 0.20))
  training3_19 = train3.randomColumn('x',19).filter(ee.Filter.lt('x', 0.20))

  # train and deploy model
  vote1 = deploy(train2, training3_1, trainImage, deployImage)
  vote2 = deploy(train2, training3_2, trainImage, deployImage)
  vote3 = deploy(train2, training3_3, trainImage, deployImage)
  vote4 = deploy(train2, training3_4, trainImage, deployImage)
  vote5 = deploy(train2, training3_5, trainImage, deployImage)
  vote6 = deploy(train2, training3_6, trainImage, deployImage)
  vote7 = deploy(train2, training3_7, trainImage, deployImage)
  vote8 = deploy(train2, training3_8, trainImage, deployImage)
  vote9 = deploy(train2, training3_9, trainImage, deployImage)
  vote10 = deploy(train2, training3_10, trainImage, deployImage)
  vote11 = deploy(train2, training3_11, trainImage, deployImage)
  vote12 = deploy(train2, training3_12, trainImage, deployImage)
  vote13 = deploy(train2, training3_13, trainImage, deployImage)
  vote14 = deploy(train2, training3_14, trainImage, deployImage)
  vote15 = deploy(train2, training3_15, trainImage, deployImage)
  vote16 = deploy(train2, training3_16, trainImage, deployImage)
  vote17 = deploy(train2, training3_17, trainImage, deployImage)
  vote18 = deploy(train2, training3_18, trainImage, deployImage)
  vote19 = deploy(train2, training3_19, trainImage, deployImage)

  # combine votes
  votes = vote1.addBands(vote2).addBands(vote3).addBands(vote4).addBands(vote5).addBands(vote6).addBands(vote7).addBands(vote8).addBands(vote9).addBands(vote10).addBands(vote11).addBands(vote12).addBands(vote13).addBands(vote14).addBands(vote15).addBands(vote16).addBands(vote17).addBands(vote18).addBands(vote19)
  result = votes.reduce('mean')
  result = result.addBands(result.select('mean').round().rename('result'))
  result = result.addBands(result.select('mean').subtract(2).rename('confidence'))
  fixMask = result.select('confidence').eq(0)
  fixedConfidence = result.select('confidence').add(fixMask)

  result = result.select('mean', 'result').addBands(fixedConfidence)

  return result