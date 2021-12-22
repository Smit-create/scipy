import cupy as cp
import numpy as np
import scipy.signal as _scipy_signal
import cusignal as _cusignal

# Backend support for scipy.signal

__ua_domain__ = 'numpy.scipy.signal'
_implemented = {}


def __ua_convert__(dispatchables, coerce):
    if coerce:
        try:
            replaced = [
                cp.asarray(d.value) if d.coercible and d.type is np.ndarray
                else d.value for d in dispatchables
            ]
        except TypeError:
            return NotImplementedError
    elif dispatchables == None:
        # handling for no dispatchables
        replaced = []
    else:
        replaced = [d.value for d in dispatchables]

    return replaced


def __ua_function__(method, args, kwargs):
    fn = _implemented.get(method, None)
    if fn is None:
        return NotImplementedError

    return fn(*args, **kwargs)


def _implements(scipy_func):
    """Decorator adds function to the dictionary of implemented functions"""
    def inner(func):
        _implemented[scipy_func] = func
        return func

    return inner


@_implements(_scipy_signal.upfirdn)
def upfirdn(h, x, up=1, down=1, axis=-1, mode='constant', cval=0):
    return _cusignal.upfirdn(h, x, up=up, down=down, axis=axis)
upfirdn.__doc__ = _cusignal.upfirdn.__doc__
