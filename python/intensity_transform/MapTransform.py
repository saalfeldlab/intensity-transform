from ij.process import ShortProcessor
from ij.process import FloatProcessor

from mpicbg.models import TranslationModel2D
from mpicbg.models import CoordinateTransformList
from mpicbg.models import CoordinateTransformMesh

from mpicbg.trakem2.transform import TransformMeshMappingWithMasks

class MapTransform(object):
    @staticmethod
    def doMap(patch, roi, background=0.0, interpolate=False, floatp=False):
        if floatp:
            target = FloatProcessor(roi.width, roi.height)
        else:
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

        source = patch.getImageProcessor()
        if floatp:
            source = source.convertToFloatProcessor()
        if interpolate:
            # patch.getImageProcessor().setInterpolationMethod( ImageProcessor.BILINEAR )
            mapping.mapInterpolated( source, target )
        else:
            mapping.map( source, target )

        return target
