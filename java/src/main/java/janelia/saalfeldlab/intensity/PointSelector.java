package janelia.saalfeldlab.intensity;

import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;

public interface PointSelector<T extends RealType<T>, U extends RealType<U>,
         					   V extends IntegerType<V>, W extends IntegerType<W> > {
	
	boolean isGood(T i1, U i2, V l1, W l2);
}
