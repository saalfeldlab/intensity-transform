from intensity_transform import *

from collections import defaultdict

import errno

from ij import ImagePlus

from ini.trakem2.display import Patch, Layer, Display
from ini.trakem2.persistence import FSLoader

from org.janelia.alignment.intensity import PointSelectorIgnoreBackground
from org.janelia.alignment.intensity import PointSelectorIgnoreBackgroundAndOutliers
from org.janelia.alignment.intensity import PointMatchGenerator
from org.janelia.alignment.intensity import ApplyTransform

from jarray import zeros

from java.io import File
from java.lang import Long
from java.util import ArrayList

from mpicbg.models import AffineModel1D
from mpicbg.models import IdentityModel
from mpicbg.models import InterpolatedAffineModel1D
from mpicbg.models import NotEnoughDataPointsException
from mpicbg.models import Tile
from mpicbg.models import TileConfiguration 
from mpicbg.models import TranslationModel1D

from mpicbg.trakem2.transform import ExportUnsignedShort

from mpicbg.ij.util import Filter

from net.imglib2.img import ImagePlusAdapter
from net.imglib2.type.numeric.integer import UnsignedShortType
from net.imglib2.type.numeric.real import FloatType

import os

import time



display = Display.getFront()

shape = (3, 3)

subscriptToIndex = [None] * (shape[0]*shape[1])
helperIndex = 0
for x in xrange(shape[0]):
    for y in xrange(shape[1]):
        subscriptToIndex[helperIndex] = (x, y)
        helperIndex += 1


# use coordinate transform folder to specify output folder
ctsFolder     = display.project.getLoader().getCoordinateTransformsFolder().rstrip('/')
lastFolderIdx = len(ctsFolder.split('/')) - 1
itsFolder     = '/'.join(ctsFolder.split('/')[:-1]) + '/trakem2.its/'
File(itsFolder).mkdirs()


# At the moment, all overlays, PointMatches, etc. are kept in memory while iterating over all layers.
# In future, memory should be released after saving the result.

# For each layer store (without amibugity) the patch matches for each patch in a dictionary:
# { layer : { patch : [(match, intersection), ...] } }
patchMatchesPerLayer  = defaultdict(lambda : defaultdict(list) )

# For each layer and patch store the appropriate overlay:
# { layer : { patch : overlay } }
overlaysPerLayer      = defaultdict(dict)

# For each layer store for each tile at each patch the list of point matches:
# { layer : { patch : { tile : [PointMatch, ...] } } }
matchedPointsPerLayer = defaultdict(lambda : defaultdict(lambda : defaultdict(list) ) )

# For each layer and patch store the appropriate tile:
# { layer : { patch : { id : Tile } } }
tiles                 = defaultdict(lambda : defaultdict(dict))

# { layer : { Patch : inverseMap } }
inverseMapTransforms  = defaultdict(dict)


tileConfigs           = {}

lambda1 = 0.1
lambda2 = 0.1

# selector and generator now specific for patch/match pairs
# pointSelector       = PointSelectorIgnoreBackground(UnsignedShortType(0), UnsignedShortType(0))
# pointMatchGenerator = PointMatchGenerator(pointSelector)

scaleFactor = 0.1

intraPatchSimilarityRegularizationWeight = 1.0

optimizationOptions = { 'error' : 100.0, 'maxIterations' : 10, 'maxPlateau' : 10 }


class AddTime(object):
    def __init__(self):
        self.t0 = time.time()

    def addString(self):
        return "t=%f" % (time.time() - self.t0)

addTime = AddTime()

print "Collect intersecting patches (%s) ... " % addTime.addString()

for layer in display.getLayerSet().getLayers():
    patchMatchesAtLayer = patchMatchesPerLayer[layer]
    overlaysAtLayer     = overlaysPerLayer[layer]
    getIntersectingPatches(display.project, layer, patchMatchesAtLayer, overlaysAtLayer, shape)


print "Generate tiles (%s) ... " % addTime.addString()

for layer, patches in patchMatchesPerLayer.iteritems():
    for patch, matches in patches.iteritems():
        for x in xrange(1, shape[0]*shape[1] + 1):
            model = InterpolatedAffineModel1D(AffineModel1D(), InterpolatedAffineModel1D(TranslationModel1D(), IdentityModel(), lambda1), lambda2)
            # model = TranslationModel1D()
            tiles[layer][patch][x] = Tile(model)


print "Extract point matches (%s) ... " % addTime.addString()

for layer, patches in patchMatchesPerLayer.iteritems():
    overlays = overlaysPerLayer[layer]
    matchedPoints  = matchedPointsPerLayer[layer]
    tilesAt = tiles[layer]
    for patch, matches in patches.iteritems():
        matchedPointsAtPatch = matchedPoints[patch]
        tilesAtPatch         = tilesAt[patch]
        patchPreTransform    = getPreTransform(patch)
        
        inverseMapTransforms[layer][patch] = InverseMapTransform(patchPreTransform[0], patchPreTransform[1], 255)

        for match in matches:
            matchPreTransform   = getPreTransform(match[0])
            # saturated and zero value pixels should be ignored
            # pixels that are within the intersection bb but not part of any patch are to be ignored
            pointSelector       = PointSelectorIgnoreBackgroundAndOutliers(FloatType(patch.getImagePlus().getProcessor().minValue()),
                                                                           FloatType(patch.getImagePlus().getProcessor().maxValue()),
                                                                           FloatType(match[0].getImagePlus().getProcessor().minValue()),
                                                                           FloatType(match[0].getImagePlus().getProcessor().maxValue()),
                                                                           UnsignedShortType(0),
                                                                           UnsignedShortType(0))
            # extract points from transformed patches
            pointMatchGenerator = PointMatchGenerator(pointSelector,
                                                      FloatType(patchPreTransform[0]),
                                                      FloatType(patchPreTransform[1]),
                                                      FloatType(matchPreTransform[0]),
                                                      FloatType(matchPreTransform[1]))

            
            tilesAtMatch = tilesAt[match[0]]
            bb = match[1].getBounds()

            # maybe set floatp=False for all of these
            ip1a = MapTransform.doMap(patch, bb, interpolate=True, floatp=False)
            ip1b = MapTransform.doMap(overlays[patch], bb)
            ip2a = MapTransform.doMap(match[0], bb, interpolate=True, floatp=False)
            ip2b = MapTransform.doMap(overlays[match[0]], bb)

            # show images for debugging purposes
            # ImagePlus("", ip1a).show()
            # ImagePlus("", ip2a).show()
            
            imp1a = ImagePlus("%s" % patch, Filter.scale(ip1a, scaleFactor))
            imp1b = ImagePlus("%s" % overlays[patch], ip1b.resize(Math.round( scaleFactor*ip1b.getWidth() ), Math.round( scaleFactor*ip1b.getHeight() ) ) )
            imp2a = ImagePlus("%s" % match[0], Filter.scale(ip2a, scaleFactor))
            imp2b = ImagePlus("%s" % overlays[match[0]], ip2b.resize(Math.round( scaleFactor*ip2b.getWidth() ), Math.round( scaleFactor*ip2b.getHeight() ) ) ) 

            # show images for debugging purposes
            # imp1a.show()
            # imp1b.show()
            # imp2a.show()
            # imp2b.show()

            

            img1a = ImagePlusAdapter.wrap(imp1a)
            img1b = ImagePlusAdapter.wrap(imp1b)
            img2a = ImagePlusAdapter.wrap(imp2a)
            img2b = ImagePlusAdapter.wrap(imp2b)

            pointMatchGenerator.generate(img1a, img2a, img1b, img2b)
            pointHashMap = pointMatchGenerator.getPointMatches()

            for entryset in pointHashMap.entrySet():
                pointMatches = entryset.getValue()

                # connect tile at patch/grid position to tile at match/grid position with appropriate pointMatches
                # remove outliers first (ransac)

                pairWiseModel = AffineModel1D()
                inliers       = ArrayList()
                
                try:
                    pairWiseModel.filterRansac( pointMatches, inliers, 1000, 5, 0.1, 20, 2 )
                    tilesAtPatch[entryset.getKey().a].connect(tilesAtMatch[entryset.getKey().b], inliers)
                except NotEnoughDataPointsException:
                    pass


print "Add smoothness constraint between (neighboring) tiles within a patch (%s) ... " % addTime.addString()

for layer, ts in tiles.iteritems():
    tilesAt = tiles[layer]
    for patch, tileList in ts.iteritems():
        tilesAtPatch = tilesAt[patch]
        for x in xrange(shape[0]):
            for y in xrange(shape[1]):
                pointMatches = ArrayList(2)
                pointMatches.add(PointMatch(1.0, 1.0, intraPatchSimilarityRegularizationWeight))
                pointMatches.add(PointMatch(0.0, 0.0, intraPatchSimilarityRegularizationWeight))
                currIndex = x + shape[0] * y
                # actual index + 1, as tiles do not have zero index in order to avoid confusion with background
                # cf loop starting after 'print "Generate tiles (%s) ... " % addTime.addString()'
                if x + 1 < shape[0]:
                    neighborIndex = currIndex + 1
                    tilesAtPatch[currIndex + 1].connect(tilesAtPatch[neighborIndex + 1], pointMatches)
                if y + 1 < shape[1]:
                    neighborIndex = currIndex + shape[0]
                    tilesAtPatch[currIndex + 1].connect(tilesAtPatch[neighborIndex + 1], pointMatches)
                    

print "Add tiles to TileConfiguration if enough point matches and optimize (%s) ... " % addTime.addString()

for layer, ts in tiles.iteritems():
    tc = TileConfiguration()
    for patch, tileList in ts.iteritems():
        for t in tileList.values():
            if t.getMatches().size() < 2:
                continue
            tc.addTile(t)

    print "Before optimization (%s) ... " % addTime.addString()
    tc.optimize( optimizationOptions['error'], optimizationOptions['maxIterations'], optimizationOptions['maxPlateau'] )
    print "After optimization (%s) ... " %addTime.addString()


# print "Write transformed images to file (%s) ... " % addTime.addString()
print "Saving files into directory %s (%s) ... " % (itsFolder, addTime.addString())

for layer, ts in tiles.iteritems():
    for patch, tileList in ts.iteritems():
        ifp    = patch.getImageFilePath()
        ifpArr = ifp.split( '/' )
        newDir = '/'.join(ifpArr[:-1]) + '/transforms'
        newFn  = newDir + '/%s' % ifpArr[-1]
        width  = shape[0]
        height = shape[1]
        stepX  = 1
        stepY  = 1

        filePath = itsFolder + display.project.getLoader().createIdPath(Long.toString(patch.getCoordinateTransformId()),
                                                                        Long.toString(patch.getId()),
                                                                        '.it')
        resultStack = ImageStack( width, height, 2 )
        parameter1p = FloatProcessor( width, height )
        parameter2p = FloatProcessor( width, height )
        resultStack.setProcessor( parameter1p, 1 )
        resultStack.setProcessor( parameter2p, 2 )
        resultImage = ImagePlus("", resultStack)
        for idx, t in sorted( tileList.iteritems(), key=lambda x : x[0] ):
            model = zeros( 2, 'd' )
            t.getModel().toArray( model )
            x, y = subscriptToIndex[idx - 1]
            parameter1p.setf(x, y, inverseMapTransforms[layer][patch].getNewLinearTerm(model[0]))
            parameter2p.setf(x, y, inverseMapTransforms[layer][patch].getNewConstantTerm(model[0], model[1]))
        IJ.saveAsTiff( resultImage, filePath )


# visualization check for two patches and one tile per patch
# comment out for application on real data!

# from jarray import zeros

# for layer, ts in tiles.iteritems():
#     for patch, tileList in ts.iteritems():
#         bb = patch.getBoundingBox()
#         img = ImagePlus("%s" % patch, ExportUnsignedShort.makeFlatImage([patch], bb))
#         for idx, t in sorted(tileList.iteritems(), key=lambda x: x[0]):
#             a = zeros(2, 'd')
#             t.getModel().toArray( a )
#             print "  ", idx, a
#             tf = ApplyTransform( a )
#             tf.apply(img)
#             img.show()
