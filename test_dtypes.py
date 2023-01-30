# -*- coding: utf-8 -*-
from itertools import product

import nose
import numpy as np
from pandas import Series, Categorical, date_range
import pandas.core.common as com
from pandas.types.api import CategoricalDtype
from pandas.core.common import (is_categorical_dtype,
                                is_categorical, DatetimeTZDtype,
                                is_datetime64tz_dtype, is_datetimetz,
                                is_dtype_equal, is_datetime64_ns_dtype,
                                is_datetime64_dtype)
import pandas.util.testing as tm

_multiprocess_can_split_ = True


class Base(object):

    def test_hash(self):
        hash(self.dtype)

    def test_equality_invalid(self):
        self.assertRaises(self.dtype == 'foo')

    def test_numpy_informed(self):

        # np.dtype doesn't know about our new dtype
        def f():
            np.dtype(self.dtype)

        self.assertRaises(TypeError, f)

        self.assertNotEqual(self.dtype, np.str_)
        self.assertNotEqual(np.str_, self.dtype)

    def test_pickle(self):
        result = self.round_trip_pickle(self.dtype)
        self.assertEqual(result, self.dtype)


class TestCategoricalDtype(Base, tm.TestCase):

    def setUp(self):
        self.dtype = CategoricalDtype()

    def test_equality(self):
        self.assertTrue(is_dtype_equal(self.dtype, 'category'))
        self.assertTrue(is_dtype_equal(self.dtype, CategoricalDtype()))
        self.assertFalse(is_dtype_equal(self.dtype, 'foo'))

    def test_construction_from_string(self):
        result = CategoricalDtype.construct_from_string('category')
        self.assertTrue(is_dtype_equal(self.dtype, result))
        self.assertRaises(
            TypeError, lambda: CategoricalDtype.construct_from_string('foo'))

    def test_is_dtype(self):
        self.assertTrue(CategoricalDtype.is_dtype(self.dtype))
        self.assertTrue(CategoricalDtype.is_dtype('category'))
        self.assertTrue(CategoricalDtype.is_dtype(CategoricalDtype()))
        self.assertFalse(CategoricalDtype.is_dtype('foo'))
        self.assertFalse(CategoricalDtype.is_dtype(np.float64))

    def test_basic(self):

        self.assertTrue(is_categorical_dtype(self.dtype))

        factor = Categorical.from_array(['a', 'b', 'b', 'a', 'a', 'c', 'c', 'c'
                                         ])

        s = Series(factor, name='A')

        # dtypes
        self.assertTrue(is_categorical_dtype(s.dtype))
        self.assertTrue(is_categorical_dtype(s))
        self.assertFalse(is_categorical_dtype(np.dtype('float64')))

        self.assertTrue(is_categorical(s.dtype))
        self.assertTrue(is_categorical(s))
        self.assertFalse(is_categorical(np.dtype('float64')))
        self.assertFalse(is_categorical(1.0))


class TestDatetimeTZDtype(Base, tm.TestCase):

    def setUp(self):
        self.dtype = DatetimeTZDtype('ns', 'US/Eastern')

    def test_construction(self):
        self.assertRaises(ValueError,
                          lambda: DatetimeTZDtype('ms', 'US/Eastern'))

    def test_subclass(self):
        a = DatetimeTZDtype('datetime64[ns, US/Eastern]')
        b = DatetimeTZDtype('datetime64[ns, CET]')

        self.assertTrue(issubclass(type(a), type(a)))
        self.assertTrue(issubclass(type(a), type(b)))

    def test_coerce_to_dtype(self):
        self.assertEqual(com._coerce_to_dtype('datetime64[ns, US/Eastern]'),
                         DatetimeTZDtype('ns', 'US/Eastern'))
        self.assertEqual(com._coerce_to_dtype('datetime64[ns, Asia/Tokyo]'),
                         DatetimeTZDtype('ns', 'Asia/Tokyo'))

    def test_compat(self):
        self.assertFalse(is_datetime64_ns_dtype(self.dtype))
        self.assertFalse(is_datetime64_ns_dtype('datetime64[ns, US/Eastern]'))
        self.assertFalse(is_datetime64_dtype(self.dtype))
        self.assertFalse(is_datetime64_dtype('datetime64[ns, US/Eastern]'))

    def test_construction_from_string(self):
        result = DatetimeTZDtype('datetime64[ns, US/Eastern]')
        self.assertTrue(is_dtype_equal(self.dtype, result))
        result = DatetimeTZDtype.construct_from_string(
            'datetime64[ns, US/Eastern]')
        self.assertTrue(is_dtype_equal(self.dtype, result))
        self.assertRaises(TypeError,
                          lambda: DatetimeTZDtype.construct_from_string('foo'))

    def test_is_dtype(self):
        self.assertTrue(DatetimeTZDtype.is_dtype(self.dtype))
        self.assertTrue(DatetimeTZDtype.is_dtype('datetime64[ns, US/Eastern]'))
        self.assertFalse(DatetimeTZDtype.is_dtype('foo'))
        self.assertTrue(DatetimeTZDtype.is_dtype(DatetimeTZDtype(
            'ns', 'US/Pacific')))
        self.assertFalse(DatetimeTZDtype.is_dtype(np.float64))

    def test_equality(self):
        self.assertTrue(is_dtype_equal(self.dtype,
                                       'datetime64[ns, US/Eastern]'))
        self.assertTrue(is_dtype_equal(self.dtype, DatetimeTZDtype(
            'ns', 'US/Eastern')))
        self.assertFalse(is_dtype_equal(self.dtype, 'foo'))
        self.assertFalse(is_dtype_equal(self.dtype, DatetimeTZDtype('ns',
                                                                    'CET')))
        self.assertFalse(is_dtype_equal(
            DatetimeTZDtype('ns', 'US/Eastern'), DatetimeTZDtype(
                'ns', 'US/Pacific')))

        # numpy compat
        self.assertTrue(is_dtype_equal(np.dtype("M8[ns]"), "datetime64[ns]"))

    def test_basic(self):

        self.assertTrue(is_datetime64tz_dtype(self.dtype))

        dr = date_range('20130101', periods=3, tz='US/Eastern')
        s = Series(dr, name='A')

        # dtypes
        self.assertTrue(is_datetime64tz_dtype(s.dtype))
        self.assertTrue(is_datetime64tz_dtype(s))
        self.assertFalse(is_datetime64tz_dtype(np.dtype('float64')))
        self.assertFalse(is_datetime64tz_dtype(1.0))

        self.assertTrue(is_datetimetz(s))
        self.assertTrue(is_datetimetz(s.dtype))
        self.assertFalse(is_datetimetz(np.dtype('float64')))
        self.assertFalse(is_datetimetz(1.0))

    def test_dst(self):

        dr1 = date_range('2013-01-01', periods=3, tz='US/Eastern')
        s1 = Series(dr1, name='A')
        self.assertTrue(is_datetimetz(s1))

        dr2 = date_range('2013-08-01', periods=3, tz='US/Eastern')
        s2 = Series(dr2, name='A')
        self.assertTrue(is_datetimetz(s2))
        self.assertEqual(s1.dtype, s2.dtype)

    def test_parser(self):
        # pr #11245
        for tz, constructor in product(('UTC', 'US/Eastern'),
                                       ('M8', 'datetime64')):
            self.assertEqual(
                DatetimeTZDtype('%s[ns, %s]' % (constructor, tz)),
                DatetimeTZDtype('ns', tz),
            )


if __name__ == '__main__':
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
p(TypeError, 'include and exclude .+ non-'):
            df.select_dtypes(exclude='object')
        with tm.assertRaisesRegexp(TypeError, 'include and exclude .+ non-'):
            df.select_dtypes(include=int, exclude='object')

    def test_select_dtypes_bad_datetime64(self):
        df = DataFrame({'a': list('abc'),
                        'b': list(range(1, 4)),
                        'c': np.arange(3, 6).astype('u1'),
                        'd': np.arange(4.0, 7.0, dtype='float64'),
                        'e': [True, False, True],
                        'f': pd.date_range('now', periods=3).values})
        with tm.assertRaisesRegexp(ValueError, '.+ is too specific'):
            df.select_dtypes(include=['datetime64[D]'])

        with tm.assertRaisesRegexp(ValueError, '.+ is too specific'):
            df.select_dtypes(exclude=['datetime64[as]'])

    def test_select_dtypes_str_raises(self):
        df = DataFrame({'a': list('abc'),
                        'g': list(u('abc')),
                        'b': list(range(1, 4)),
                        'c': np.arange(3, 6).astype('u1'),
                        'd': np.arange(4.0, 7.0, dtype='float64'),
                        'e': [True, False, True],
                        'f': pd.date_range('now', periods=3).values})
        string_dtypes = set((str, 'str', np.string_, 'S1',
                             'unicode', np.unicode_, 'U1'))
        try:
            string_dtypes.add(unicode)
        except NameError:
            pass
        for dt in string_dtypes:
            with tm.assertRaisesRegexp(TypeError,
                                       'string dtypes are not allowed'):
                df.select_dtypes(include=[dt])
            with tm.assertRaisesRegexp(TypeError,
                                       'string dtypes are not allowed'):
                df.select_dtypes(exclude=[dt])

    def test_select_dtypes_bad_arg_raises(self):
        df = DataFrame({'a': list('abc'),
                        'g': list(u('abc')),
                        'b': list(range(1, 4)),
                        'c': np.arange(3, 6).astype('u1'),
                        'd': np.arange(4.0, 7.0, dtype='float64'),
                        'e': [True, False, True],
                        'f': pd.date_range('now', periods=3).values})
        with tm.assertRaisesRegexp(TypeError, 'data type.*not understood'):
            df.select_dtypes(['blargy, blarg, blarg'])

    def test_select_dtypes_typecodes(self):
        # GH 11990
        df = mkdf(30, 3, data_gen_f=lambda x, y: np.random.random())
        expected = df
        FLOAT_TYPES = list(np.typecodes['AllFloat'])
        assert_frame_equal(df.select_dtypes(FLOAT_TYPES), expected)

    def test_dtypes_gh8722(self):
        self.mixed_frame['bool'] = self.mixed_frame['A'] > 0
        result = self.mixed_frame.dtypes
        expected = Series(dict((k, v.dtype)
                               for k, v in compat.iteritems(self.mixed_frame)),
                          index=result.index)
        assert_series_equal(result, expected)

        # compat, GH 8722
        with option_context('use_inf_as_null', True):
            df = DataFrame([[1]])
            result = df.dtypes
            assert_series_equal(result, Series({0: np.dtype('int64')}))

    def test_ftypes(self):
        frame = self.mixed_float
        expected = Series(dict(A='float32:dense',
                               B='float32:dense',
                               C='float16:dense',
                               D='float64:dense')).sort_values()
        result = frame.ftypes.sort_values()
        assert_series_equal(result, expected)

    def test_astype(self):
        casted = self.frame.astype(int)
        expected = DataFrame(self.frame.values.astype(int),
                             index=self.frame.index,
                             columns=self.frame.columns)
        assert_frame_equal(casted, expected)

        casted = self.frame.astype(np.int32)
        expected = DataFrame(self.frame.values.astype(np.int32),
                             index=self.frame.index,
                             columns=self.frame.columns)
        assert_frame_equal(casted, expected)

        self.frame['foo'] = '5'
        casted = self.frame.astype(int)
        expected = DataFrame(self.frame.values.astype(int),
                             index=self.frame.index,
                             columns=self.frame.columns)
        assert_frame_equal(casted, expected)

        # mixed casting
        def _check_cast(df, v):
            self.assertEqual(
                list(set([s.dtype.name
                          for _, s in compat.iteritems(df)]))[0], v)

        mn = self.all_mixed._get_numeric_data().copy()
        mn['little_float'] = np.array(12345., dtype='float16')
        mn['big_float'] = np.array(123456789101112., dtype='float64')

        casted = mn.astype('float64')
        _check_cast(casted, 'float64')

        casted = mn.astype('int64')
        _check_cast(casted, 'int64')

        casted = self.mixed_float.reindex(columns=['A', 'B']).astype('float32')
        _check_cast(casted, 'float32')

        casted = mn.reindex(columns=['little_float']).astype('float16')
        _check_cast(casted, 'float16')

        casted = self.mixed_float.reindex(columns=['A', 'B']).astype('float16')
        _check_cast(casted, 'float16')

        casted = mn.astype('float32')
        _check_cast(casted, 'float32')

        casted = mn.astype('int32')
        _check_cast(casted, 'int32')

        # to object
        casted = mn.astype('O')
        _check_cast(casted, 'object')

    def test_astype_with_exclude_string(self):
        df = self.frame.copy()
        expected = self.frame.astype(int)
        df['string'] = 'foo'
        casted = df.astype(int, raise_on_error=False)

        expected['string'] = 'foo'
        assert_frame_equal(casted, expected)

        df = self.frame.copy()
        expected = self.frame.astype(np.int32)
        df['string'] = 'foo'
        casted = df.astype(np.int32, raise_on_error=False)

        expected['string'] = 'foo'
        assert_frame_equal(casted, expected)

    def test_astype_with_view(self):

        tf = self.mixed_float.reindex(columns=['A', 'B', 'C'])

        casted = tf.astype(np.int64)

        casted = tf.astype(np.float32)

        # this is the only real reason to do it this way
        tf = np.round(self.frame).astype(np.int32)
        casted = tf.astype(np.float32, copy=False)

        # TODO(wesm): verification?
        tf = self.frame.astype(np.float64)
        casted = tf.astype(np.int64, copy=False)  # noqa

    def test_astype_cast_nan_int(self):
        df = DataFrame(data={"Values": [1.0, 2.0, 3.0, np.nan]})
        self.assertRaises(ValueError, df.astype, np.int64)

    def test_astype_str(self):
        # GH9757
        a = Series(date_range('2010-01-04', periods=5))
        b = Series(date_range('3/6/2012 00:00', periods=5, tz='US/Eastern'))
        c = Series([Timedelta(x, unit='d') for x in range(5)])
        d = Series(range(5))
        e = Series([0.0, 0.2, 0.4, 0.6, 0.8])

        df = DataFrame({'a': a, 'b': b, 'c': c, 'd': d, 'e': e})

        # datetimelike
        # Test str and unicode on python 2.x and just str on python 3.x
        for tt in set([str, compat.text_type]):
            result = df.astype(tt)

            expected = DataFrame({
                'a': list(map(tt, map(lambda x: Timestamp(x)._date_repr,
                                      a._values))),
                'b': list(map(tt, map(Timestamp, b._values))),
                'c': list(map(tt, map(lambda x: Timedelta(x)
                                      ._repr_base(format='all'), c._values))),
                'd': list(map(tt, d._values)),
                'e': list(map(tt, e._values)),
            })

            assert_frame_equal(result, expected)

        # float/nan
        # 11302
        # consistency in astype(str)
        for tt in set([str, compat.text_type]):
            result = DataFrame([np.NaN]).astype(tt)
            expected = DataFrame(['nan'])
            assert_frame_equal(result, expected)

            result = DataFrame([1.12345678901234567890]).astype(tt)
            expected = DataFrame(['1.12345678901'])
            assert_frame_equal(result, expected)

    def test_timedeltas(self):
        df = DataFrame(dict(A=Series(date_range('2012-1-1', periods=3,
                                                freq='D')),
                            B=Series([timedelta(days=i) for i in range(3)])))
        result = df.get_dtype_counts().sort_values()
        expected = Series(
            {'datetime64[ns]': 1, 'timedelta64[ns]': 1}).sort_values()
        assert_series_equal(result, expected)

        df['C'] = df['A'] + df['B']
        expected = Series(
            {'datetime64[ns]': 2, 'timedelta64[ns]': 1}).sort_values()
        result = df.get_dtype_counts().sort_values()
        assert_series_equal(result, expected)

        # mixed int types
        df['D'] = 1
        expected = Series({'datetime64[ns]': 2,
                           'timedelta64[ns]': 1,
                           'int64': 1}).sort_values()
        result = df.get_dtype_counts().sort_values()
        assert_series_equal(result, expected)
