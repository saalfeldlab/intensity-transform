/**
 * 
 */
package org.janelia.alignment.intensity;

import java.util.Collection;
import java.util.List;

import mpicbg.models.AffineModel1D;
import mpicbg.models.Model;
import mpicbg.models.Point;
import mpicbg.models.PointMatch;

/**
 * @author Stephan Saalfeld <saalfelds@janelia.hhmi.org>
 *
 */
public class RansacRegressionReduceFilter implements PointMatchFilter
{
	final protected Model< ? > model = new AffineModel1D();
	final protected int iterations = 1000;
	final protected float  maxEpsilon = 0.1f;
	final protected float minInlierRatio = 0.1f;
	final protected int minNumInliers = 10;
	final protected float maxTrust = 3.0f;
	
	@Override
	public void filter( List< PointMatch > candidates, Collection< PointMatch > inliers )
	{
		try
		{
			if (
					model.filterRansac(
							candidates,
							inliers,
							iterations,
							maxEpsilon,
							minInlierRatio,
							minNumInliers,
							maxTrust ) )
			{
				model.fit( inliers );
				
				inliers.clear();
				
				final Point p1 = new Point( new float[]{ 0 } );
				final Point p2 = new Point( new float[]{ 1 } );
				p1.apply( model );
				p2.apply( model );
				inliers.add( new PointMatch( p1, new Point( p1.getW().clone() ) ) );
				inliers.add( new PointMatch( p2, new Point( p2.getW().clone() ) ) );
			}
			else
					inliers.clear();
		}
		catch ( Exception e )
		{
			inliers.clear();
		}
	}

}
