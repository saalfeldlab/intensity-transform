package org.janelia.alignment.intensity;

import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;

public class PointSelectorIgnoreBackgroundAndOutliers<T extends RealType<T>, U extends RealType<U>,
V extends IntegerType<V>, W extends IntegerType<W> > implements PointSelector<T, U, V, W> {

	private final T min1;
	private final T max1;
	
	private final U min2;
	private final U max2;
	
	private final V bg1;
	private final W bg2;
	
	

	public PointSelectorIgnoreBackgroundAndOutliers(T min1, T max1, U min2,
			U max2, V bg1, W bg2) {
		super();
		this.min1 = min1;
		this.max1 = max1;
		this.min2 = min2;
		this.max2 = max2;
		this.bg1 = bg1;
		this.bg2 = bg2;
	}



	@Override
	public boolean isGood(T i1, U i2, V l1, W l2) {
//	public boolean isGood(RealType i1, RealType i2, IntegerType l1,
//			IntegerType l2) {
		if (i1.getRealDouble() <= min1.getRealDouble() || i1.getRealDouble() >= max1.getRealDouble() ||
			i2.getRealDouble() <= min2.getRealDouble() || i2.getRealDouble() >= max2.getRealDouble() ||
			l1.getIntegerLong() == bg1.getIntegerLong() || l2.getIntegerLong() == bg2.getIntegerLong()) {
			return false;
		}
		return true;
	}

}
