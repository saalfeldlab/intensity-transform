/**
 * License: GPL
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License 2
 * as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
package org.janelia.alignment.intensity;

import ij.ImageJ;
import ij.ImagePlus;
import net.imglib2.Cursor;
import net.imglib2.Dimensions;
import net.imglib2.FinalInterval;
import net.imglib2.IterableInterval;
import net.imglib2.RandomAccessible;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.RealRandomAccessible;
import net.imglib2.img.array.ArrayImg;
import net.imglib2.img.array.ArrayImgs;
import net.imglib2.img.basictypeaccess.array.FloatArray;
import net.imglib2.img.display.imagej.ImageJFunctions;
import net.imglib2.interpolation.randomaccess.NLinearInterpolatorFactory;
import net.imglib2.realtransform.RealViews;
import net.imglib2.realtransform.Scale;
import net.imglib2.realtransform.Translation;
import net.imglib2.type.numeric.RealType;
import net.imglib2.type.numeric.real.DoubleType;
import net.imglib2.type.numeric.real.FloatType;
import net.imglib2.view.Views;
import net.imglib2.view.composite.CompositeIntervalView;
import net.imglib2.view.composite.RealComposite;

/**
 * 
 *
 * @author Stephan Saalfeld <saalfelds@janelia.hhmi.org>
 */
public class IntensityTransform< T extends RealType< T > >
{
	final protected Dimensions dimensions;
	final protected Translation translation;
	final protected RandomAccessible< RealComposite< T > > coefficients;
	
	public IntensityTransform( final RandomAccessibleInterval< T > source )
	{
		final CompositeIntervalView< T, RealComposite< T > > collapsedSource = Views.collapseReal( source );
		dimensions = new FinalInterval( collapsedSource );
		final double[] shift = new double[ dimensions.numDimensions() ];
		for ( int d = 0; d < shift.length; ++d )
			shift[ d ] = 0.5;
		translation = new Translation( shift );
		coefficients = Views.extendBorder( collapsedSource );
	}
	
	public < S extends RealType< S > > void run( final RandomAccessibleInterval< S > image )
	{
		assert image.numDimensions() == dimensions.numDimensions() : "Number of dimensions do not match.";
		
		final double[] s = new double[ dimensions.numDimensions() ];
		for ( int d = 0; d < s.length; ++d )
			s[ d ] = image.dimension( d ) / dimensions.dimension( d );
		final Scale scale = new Scale( s );
		
		System.out.println( "translation-n " + translation.numDimensions() );
		
		final RealRandomAccessible< RealComposite< T > > interpolant = Views.interpolate( coefficients, new NLinearInterpolatorFactory< RealComposite< T > >() );
//		final RealRandomAccessible< RealComposite< T > > interpolant = Views.interpolate( coefficients, new NearestNeighborInterpolatorFactory< RealComposite< T > >() );
			
		final RandomAccessibleInterval< RealComposite< T > > stretchedCoefficients =
				Views.offsetInterval(
						Views.raster(
								RealViews.transform(
										RealViews.transform(
												interpolant,
												translation ),
										scale ) ),
						image );
		
		transform( Views.flatIterable( image ), Views.flatIterable( stretchedCoefficients ) );
	}
	
	final static protected < S extends RealType< S >, T extends RealType< T > > void transform(
			final IterableInterval< S > image,
			final IterableInterval< RealComposite< T > > coefficients )
	{
		final Cursor< S > cs = image.cursor();
		final Cursor< RealComposite< T > > ct = coefficients.cursor();
		
		while ( cs.hasNext() )
		{
			final S s = cs.next();
			final RealComposite< T > t = ct.next();
			s.setReal( s.getRealDouble() * t.get( 0 ).getRealDouble() + t.get( 1 ).getRealDouble() );
		}
	}

	public static void main( final String[] args )
	{
		new ImageJ();
		
		final double[] coefficients = new double[]{
				0, 1, 2, 3,
				1, 1, 1, 1,
				1, 10, 5, 1,
				1, 1, 1, 1,
				
				0, 10, 20, 30,
				40, 50, 60, 70,
				80, 90, 100, 110,
				120, 130, 140, 150
		};
		
		final IntensityTransform< DoubleType > transform = new IntensityTransform< DoubleType >( ArrayImgs.doubles( coefficients, 4, 4, 2 ) );
		
		final ImagePlus imp = new ImagePlus( "http://upload.wikimedia.org/wikipedia/en/2/24/Lenna.png" );
		final ImagePlus imp2 = new ImagePlus( "http://fly.mpi-cbg.de/~saalfeld/Pictures/norway.jpg");
		
		final ArrayImg< FloatType, FloatArray > image = ArrayImgs.floats( ( float[] )imp.getProcessor().convertToFloatProcessor().getPixels(), imp.getWidth(), imp.getHeight() );
		final ArrayImg< FloatType, FloatArray > image2 = ArrayImgs.floats( ( float[] )imp2.getProcessor().convertToFloatProcessor().getPixels(), imp2.getWidth(), imp2.getHeight() );
		
		ImageJFunctions.show( ArrayImgs.doubles( coefficients, 4, 4, 2 ) );
		
		transform.run( image );
		transform.run( image2 );
		
		ImageJFunctions.show( image );
		ImageJFunctions.show( image2 );
	}
}
