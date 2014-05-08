from intensity_transform import *

from collections import defaultdict

from ij import ImagePlus

from ini.trakem2.display import Patch, Layer, Display

from janelia.saalfeldlab.intensity import PointSelectorIgnoreBackground
from janelia.saalfeldlab.intensity import PointMatchGenerator
from janelia.saalfeldlab.intensity import ApplyTransform

from mpicbg.models import AffineModel1D
from mpicbg.models import IdentityModel
from mpicbg.models import InterpolatedAffineModel1D
from mpicbg.models import Tile
from mpicbg.models import TileConfiguration 
from mpicbg.models import TranslationModel1D

from mpicbg.trakem2.transform import ExportUnsignedShort

from mpicbg.ij.util import Filter

from net.imglib2.img import ImagePlusAdapter
from net.imglib2.type.numeric.integer import UnsignedShortType





display = Display.getFront()

shape = (1, 1)

patchMatchesPerLayer  = defaultdict(lambda : defaultdict(list) )
overlaysPerLayer      = defaultdict(dict)
matchedPointsPerLayer = defaultdict(lambda : defaultdict(lambda : defaultdict(list) ) )
tiles                 = defaultdict(lambda : defaultdict(dict))
tileConfigs           = {}

lambda1 = 0.1
lambda2 = 0.1

pointSelector       = PointSelectorIgnoreBackground(UnsignedShortType(0), UnsignedShortType(0))
pointMatchGenerator = PointMatchGenerator(pointSelector)

scaleFactor = 0.1

optimizationOptions = { 'error' : 0.0, 'maxIterations' : 1000, 'maxPlateau' : 1000 }


for layer in display.getLayerSet().getLayers():
    patchMatchesAtLayer = patchMatchesPerLayer[layer]
    overlaysAtLayer     = overlaysPerLayer[layer]
    getIntersectingPatches(display.project, layer, patchMatchesAtLayer, overlaysAtLayer, shape)




for layer, patches in patchMatchesPerLayer.iteritems():
    for patch, matches in patches.iteritems():
        for x in xrange(1, shape[0]*shape[1] + 1):
            model = InterpolatedAffineModel1D(AffineModel1D(), InterpolatedAffineModel1D(TranslationModel1D(), IdentityModel(), lambda1), lambda2)
            # model = TranslationModel1D()
            tiles[layer][patch][x] = Tile(model)



for layer, patches in patchMatchesPerLayer.iteritems():
    overlays = overlaysPerLayer[layer]
    matchedPoints  = matchedPointsPerLayer[layer]
    tilesAt = tiles[layer]
    for patch, matches in patches.iteritems():
        matchedPointsAtPatch = matchedPoints[patch]
        tilesAtPatch = tilesAt[patch]
        for match in matches:
            tilesAtMatch = tilesAt[match[0]]
            bb = match[1].getBounds()
            
            ip1a = ExportUnsignedShort.makeFlatImage([patch], bb)
            ip1b = MapTransform.doMap(overlays[patch], bb)
            ip2a = ExportUnsignedShort.makeFlatImage([match[0]], bb)
            ip2b = MapTransform.doMap(overlays[match[0]], bb)

            
            imp1a = ImagePlus("%s" % patch, Filter.scale(ip1a, scaleFactor))
            imp1b = ImagePlus("%s" % overlays[patch], ip1b.resize(Math.round( scaleFactor*ip1b.getWidth() ), Math.round( scaleFactor*ip1b.getHeight() ) ) )
            imp2a = ImagePlus("%s" % match[0], Filter.scale(ip2a, scaleFactor))
            imp2b = ImagePlus("%s" % overlays[match[0]], ip2b.resize(Math.round( scaleFactor*ip2b.getWidth() ), Math.round( scaleFactor*ip2b.getHeight() ) ) ) 
            
            imp1a.show()
            imp1b.show()
            imp2a.show()
            imp2b.show()

            img1a = ImagePlusAdapter.wrap(imp1a)
            img1b = ImagePlusAdapter.wrap(imp1b)
            img2a = ImagePlusAdapter.wrap(imp2a)
            img2b = ImagePlusAdapter.wrap(imp2b)

            pointMatchGenerator.generate(img1a, img2a, img1b, img2b)
            pointHashMap = pointMatchGenerator.getPointMatches()

            count = 0
            for entryset in pointHashMap.entrySet():
                tilesAtPatch[entryset.getKey().a].connect(tilesAtMatch[entryset.getKey().b], entryset.getValue())
                count += 1


for layer, ts in tiles.iteritems():
    tc = TileConfiguration()
    for patch, tileList in ts.iteritems():
        for t in tileList.values():
            if t.getMatches().size() < 2:
                continue
            tc.addTile(t)
    
    tc.optimize( optimizationOptions['error'], optimizationOptions['maxIterations'], optimizationOptions['maxPlateau'] )



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
