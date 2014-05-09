package org.janelia.alignment.intensity;

import ij.ImagePlus;
import ij.process.ByteProcessor;
import ij.process.ColorProcessor;
import ij.process.FloatProcessor;
import ij.process.ImageProcessor;
import ij.process.ShortProcessor;

public class ApplyTransform {
	
	private final double[] transform; 

	public ApplyTransform(final double[] transform) {
		assert transform.length == 2: "Transform legnth must be 2!";
		this.transform = transform;
	}
	
    public ImagePlus apply(ImagePlus img) {
    	ImageProcessor ip = img.getProcessor();
    	switch ( img.getType() )
		{
		case ImagePlus.COLOR_RGB:
			applyToRGB( ( ColorProcessor )ip );
			break;
		case ImagePlus.GRAY16:
			applyToShort( ( ShortProcessor )ip );
			break;
		case ImagePlus.GRAY32:
			applyToFloat( ( FloatProcessor )ip );
			break;
		default:
			applyToByte( ( ByteProcessor )ip );
		}
    	return img;
    }
    
    private void applyToFloat(FloatProcessor ip) {
    	final int nPixels = ip.getWidth() * ip.getHeight();
		for( int index = 0; index < nPixels; ++index )
		{
			final double val = ip.getf( index );
			final double newVal = ( this.transform[ 0 ]  * val ) + this.transform[ 1 ];
			ip.setf( index, ( float )newVal );
		}
		return;
    }
    
    private void applyToRGB(ColorProcessor ip) {
    	
    	return;
    }
    
    
    private void applyToShort(ShortProcessor ip) {
    	final int nPixels = ip.getWidth() * ip.getHeight();
		for( int index = 0; index < nPixels; ++index )
		{
			final double val = ip.getf( index );
			final double newVal = ( this.transform[ 0 ]  * val ) + this.transform[ 1 ];
			final int newValInt = newVal < 0 ? 0 : newVal > 65535 ? 65535 : ( int )Math.round( newVal );
			ip.set( index, newValInt );
		}
    	return;
    }
    
    
    private void applyToByte(ByteProcessor ip) {
    	final int nPixels = ip.getWidth() * ip.getHeight();
		for( int index = 0; index < nPixels; ++index )
		{
			final double val = ip.getf( index );
			final double newVal = ( this.transform[ 0 ]  * val ) + this.transform[ 1 ];
			final int newValInt = newVal < 0 ? 0 : newVal > 255 ? 255 : ( int )Math.round( newVal );
			ip.set( index, newValInt );
		}
    	return;
    }




}
