package janelia.saalfeldlab.intensity;

import net.imglib2.RandomAccessibleInterval;
import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;

public interface PointGenerator< T extends RealType< T >, U extends RealType< U >,
								 V extends IntegerType< V >, W extends IntegerType< W > > {
	public static class Result<T, U, V, W> {
		RandomAccessibleInterval<T> intensitySamples1;
		RandomAccessibleInterval<U> intensitySamples2;
		RandomAccessibleInterval<V> labelSamples1;
		RandomAccessibleInterval<W> labelSamples2;
	}
	
	Result<T, U, V, W> generate(RandomAccessibleInterval<T> intensities1,
			RandomAccessibleInterval<U> intensities2,
			RandomAccessibleInterval<V> labels1,
			RandomAccessibleInterval<W> labels2);

}
