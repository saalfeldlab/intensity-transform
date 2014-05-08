package janelia.saalfeldlab.intensity;

import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;

public class PointSelectorIgnoreBackground<T extends RealType<T>, U extends RealType<U>,
										   V extends IntegerType<V>, W extends IntegerType<W> > implements
		PointSelector<T, U, V, W> {

	private final IntegerType<V> background1;
	private final IntegerType<W> background2;
	
	
	
	public PointSelectorIgnoreBackground(IntegerType<V> background1,
			IntegerType<W> background2) {
		super();
		this.background1 = background1;
		this.background2 = background2;
	}





	@Override
	public boolean isGood(T i1, U i2, V l1, W l2) {
		if (l1.getIntegerLong() == this.background1.getIntegerLong() || l2.getIntegerLong() == this.background2.getIntegerLong() ) {
			return false;
		}
		return true;
	}

}
