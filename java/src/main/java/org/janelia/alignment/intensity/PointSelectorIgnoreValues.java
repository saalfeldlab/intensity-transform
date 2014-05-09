package org.janelia.alignment.intensity;

import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;

public class PointSelectorIgnoreValues<T extends RealType<T>, U extends RealType<U>,
V extends IntegerType<V>, W extends IntegerType<W> >  implements PointSelector<T, U, V, W> {

	private final V[] ignoreValues1;
	private final W[] ignoreValues2;
	
	

	public PointSelectorIgnoreValues(V[] ignoreValues1, W[] ignoreValues2) {
		super();
		this.ignoreValues1 = ignoreValues1;
		this.ignoreValues2 = ignoreValues2;
	}



	@Override
	public boolean isGood(T i1, U i2, V l1, W l2) {
		for (V v : ignoreValues1) {
			if (v.equals(l1)) {
				return false;
			}
		}
		
		for (W w : ignoreValues2) {
			if (w.equals(l2)) {
				return false;
			}
		}
		return true;
	}

}
