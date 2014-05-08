from ij.process import ShortProcessor

from mpicbg.models import TranslationModel2D
from mpicbg.models import CoordinateTransformList
from mpicbg.models import CoordinateTransformMesh

from mpicbg.trakem2.transform import TransformMeshMappingWithMasks

class MapTransform(object):
    @staticmethod
    def doMap(patch, roi, background=0.0):
        target = ShortProcessor(roi.width, roi.height)
        if background != 0.0:
            target.setValue(background)
            target.setRoi(0, 0, roi.width, roi.height)
            target.fill()
        t = TranslationModel2D()

        t.set(float(-roi.x), float(-roi.y))

        ctl = CoordinateTransformList()
        ctl.add( patch.getFullCoordinateTransform() )
        ctl.add( t )

        mesh = CoordinateTransformMesh( ctl, patch.getMeshResolution(), patch.getOWidth(), patch.getOHeight() )

        mapping = TransformMeshMappingWithMasks( mesh );

        # patch.getImageProcessor().setInterpolationMethod( ImageProcessor.BILINEAR )
        mapping.map( patch.getImageProcessor(), target )

        return target
