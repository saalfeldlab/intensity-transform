package org.janelia.alignment.intensity;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.TreeMap;

import mpicbg.models.Point;
import mpicbg.models.PointMatch;
import net.imglib2.Cursor;
import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.array.ArrayImgFactory;
import net.imglib2.type.NativeType;
import net.imglib2.type.numeric.IntegerType;
import net.imglib2.type.numeric.RealType;
import net.imglib2.util.ValuePair;
import net.imglib2.view.Views;

public class PointMatchGenerator<T extends RealType<T> & NativeType<T>, U extends RealType<U> & NativeType<U>,
                                 V extends IntegerType<V> & NativeType<V>, W extends IntegerType<W>  & NativeType<W> > implements PointGenerator<T, U, V, W> {


	public static class PairComparator implements Comparator<ValuePair<Long, Long> > {

		@Override
		public int compare(final ValuePair<Long, Long> arg0,
				final ValuePair<Long, Long> arg1) {
			if (arg0.a < arg1.a) {
				return -1;
			} else if (arg0.a > arg1.a) {
				return 1;
			} else if (arg0.b < arg1.b) {
				return -1;
			} else if (arg0.b > arg1.b) {
				return 1;
			} else {
				return 0;
			}
		}

	}


	private final TreeMap<ValuePair<Long, Long>, ArrayList<PointMatch> > pointMatches;
	private final boolean withPointList;
	private final PointSelector<T, U, V, W> selector;
	private final T min1;
	private final T range1;
	private final U min2;
	private final U range2;

	public PointMatchGenerator(final TreeMap<ValuePair<Long, Long>, ArrayList<PointMatch> > pointMatches,
			                   final boolean withPointList,
			                   final PointSelector<T, U, V, W> selector,
			                   final T min1,
			                   final T range1,
			                   final U min2,
			                   final U range2) {
		super();
		this.pointMatches  = pointMatches;
		this.withPointList = withPointList;
		this.selector      = selector;
		this.min1          = min1;
		this.range1        = range1;
		this.min2          = min2;
		this.range2        = range2;
	}

	public PointMatchGenerator(final PointSelector<T, U, V, W> selector,
                               final T min1,
                               final T range1,
                               final U min2,
                               final U range2) {
		this(new TreeMap<ValuePair<Long, Long>, ArrayList<PointMatch> >(new PairComparator()),
		     false,
		     selector,
		     min1,
		     range1,
		     min2,
		     range2);
	}

	/**
	 * @return the pointMatches
	 */
	public TreeMap<ValuePair<Long, Long>, ArrayList<PointMatch> > getPointMatches() {
		return pointMatches;
	}

	@Override
	public PointGenerator.Result<T, U, V, W> generate(
			final RandomAccessibleInterval<T> intensities1,
			final RandomAccessibleInterval<U> intensities2,
			final RandomAccessibleInterval<V> labels1,
			final RandomAccessibleInterval<W> labels2) {
	    if (this.withPointList) {
	    	return generateWithPointList(Views.flatIterable(intensities1).cursor(),
	    			Views.flatIterable(intensities2).cursor(),
	    			Views.flatIterable(labels1).cursor(),
	    			Views.flatIterable(labels2).cursor());
	    }
	    else {
	    	return generateWithoutPointList(Views.flatIterable(intensities1).cursor(),
	    			Views.flatIterable(intensities2).cursor(),
	    			Views.flatIterable(labels1).cursor(),
	    			Views.flatIterable(labels2).cursor());
	    }

	}

	private PointGenerator.Result<T, U, V, W> generateWithPointList(
			final Cursor<T> intensities1,
			final Cursor<U> intensities2,
			final Cursor<V> labels1,
			final Cursor<W> labels2) {
		final ArrayList<T> i1 = new ArrayList<T>();
		final ArrayList<U> i2 = new ArrayList<U>();
		final ArrayList<V> l1 = new ArrayList<V>();
		final ArrayList<W> l2 = new ArrayList<W>();

		while (intensities1.hasNext()) {
	    	intensities1.fwd();
	    	intensities2.fwd();
	    	labels1.fwd();
	    	labels2.fwd();

	    	if (this.selector.isGood(intensities1.get(), intensities2.get(), labels1.get(), labels2.get())) {
	    		this.pointMatches.get(new ValuePair<V, W>(labels1.get(), labels2.get())).
	    		add(new PointMatch(new Point(new double[]{intensities1.get().getRealDouble()}),
	    					           new Point(new double[]{intensities2.get().getRealDouble()}))
	    					           );
	    		i1.add(intensities1.get());
	    		i2.add(intensities2.get());
	    		l1.add(labels1.get());
	    		l2.add(labels2.get());

	    	} else {
	    		continue;
	    	}
	    }

		final PointGenerator.Result<T, U, V, W> result = new PointGenerator.Result<T, U, V, W>();


		result.intensitySamples1 = new ArrayImgFactory<T>().create(new long[]{i1.size()}, i1.get(0));
		result.intensitySamples2 = new ArrayImgFactory<U>().create(new long[]{i1.size()}, i2.get(0));
		result.labelSamples1 = new ArrayImgFactory<V>().create(new long[]{l1.size()}, l1.get(0));
		result.labelSamples2 = new ArrayImgFactory<W>().create(new long[]{l2.size()}, l2.get(0));

		{
			int index = 0;
			final Cursor<T> ic1 = Views.flatIterable(result.intensitySamples1).cursor();
			final Cursor<U> ic2 = Views.flatIterable(result.intensitySamples2).cursor();
			final Cursor<V> lc1 = Views.flatIterable(result.labelSamples1).cursor();
			final Cursor<W> lc2 = Views.flatIterable(result.labelSamples2).cursor();

			while (ic1.hasNext()) {
				ic1.next().set(i1.get(index));
				ic2.next().set(i2.get(index));
				lc1.next().set(l1.get(index));
				lc2.next().set(l2.get(index));
				++index;
			}
		}

		return result;
	}

	private PointGenerator.Result<T, U, V, W> generateWithoutPointList(
			final Cursor<T> intensities1,
			final Cursor<U> intensities2,
			final Cursor<V> labels1,
			final Cursor<W> labels2) {
	    while (intensities1.hasNext()) {
	    	intensities1.fwd();
	    	intensities2.fwd();
	    	labels1.fwd();
	    	labels2.fwd();

	    	if (this.selector.isGood(intensities1.get(), intensities2.get(), labels1.get(), labels2.get())) {
	    		final ValuePair<Long, Long> k = new ValuePair<Long, Long>(labels1.get().getIntegerLong(), labels2.get().getIntegerLong());
	    		if (!this.pointMatches.containsKey(k)) {
	    			this.pointMatches.put(k, new ArrayList<PointMatch>());
	    		}
	    		this.pointMatches.get(k).
	    			add(new PointMatch(new Point(new double[]{ ( intensities1.get().getRealDouble() - this.min1.getRealDouble()) / this.range1.getRealDouble() } ),
	    					           new Point(new double[]{ ( intensities2.get().getRealDouble() - this.min2.getRealDouble()) / this.range2.getRealDouble() } ) )
	    					           );
	    	} else {
	    		continue;
	    	}
	    }

		return null;
	}


}
