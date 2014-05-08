from ij.process import ByteProcessor

from ij import ImagePlus

from mpicbg.models import Point

from ini.trakem2.display import Patch


def getIntersectingPatches(project, layer, patchMatchesAtLayer, overlaysAtLayer, shape):
    patches = layer.getDisplayables(Patch)
    for patch in patches:
        overlaysAtLayer[patch] = generateOverlay(project, patch, shape)
        patchMatchesForPatch   = patchMatchesAtLayer[patch]
        roi                    = patch.getBoundingBox()
        intersectionCandidates = layer.getDisplayables(Patch, roi)
        for candidate in intersectionCandidates:
            intersection = patch.getIntersection(candidate)
            if not intersection.isEmpty() and not candidate in patchMatchesAtLayer.keys():
                patchMatchesForPatch.append((candidate, intersection))


def generateOverlay(project, patch, shape):
    oWidth  = patch.getOWidth()
    oHeight = patch.getOHeight()

    overlayp = ByteProcessor(oWidth, oHeight)
    # TODO: Use ShortProcessor instead of ByteProcessor
    imp      = ImagePlus("Patch %s" % patch, overlayp)
    stepX    = oWidth/shape[0]
    stepY    = oHeight/shape[1]
    color    = 1

    for x in xrange(shape[0]):
        offsetX = x * stepX
        for y in xrange(shape[1]):
            offsetY = y * stepY
            imp.setRoi(offsetX, offsetY, stepX, stepY)
            imp.getProcessor().setValue(color)
            imp.getProcessor().fill()
            color += 1
    imp.setRoi(None)
    
    overlayPatch = Patch(project, "%s_overlay" % patch, 0.0, 0.0, imp)
    
    overlayPatch.setAffineTransform(patch.getAffineTransform())
    overlayPatch.setCoordinateTransform(patch.getCoordinateTransform())
    return overlayPatch
