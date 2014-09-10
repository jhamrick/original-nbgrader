import nose.tools
import numpy as np


def assert_unequal(a, b, msg=""):
    if a == b:
        raise AssertionError(msg)


def assert_same_shape(a, b):
    a_ = np.array(a, copy=False)
    b_ = np.array(b, copy=False)
    assert a_.shape == b_.shape, "{} != {}".format(a_.shape, b_.shape)


def assert_allclose(a, b):
    assert np.allclose(a, b), "{} != {}".format(a, b)

assert_equal = nose.tools.eq_
assert_raises = nose.tools.assert_raises
