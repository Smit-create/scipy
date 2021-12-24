import cupy as cp
import numpy as np
import scipy.signal as _scipy_signal
import cupyx.scipy.signal as _cupy_signal

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
            raise NotImplementedError
    elif dispatchables == None:
        # handling for no dispatchables
        replaced = []
    else:
        replaced = [d.value for d in dispatchables]

    return replaced


def __ua_function__(method, args, kwargs):
    fn = _implemented.get(method, None)
    if fn is None:
        raise NotImplementedError

    return fn(*args, **kwargs)


def _implements(scipy_func):
    """Decorator adds function to the dictionary of implemented functions"""
    def inner(func):
        _implemented[scipy_func] = func
        return func

    return inner


@_implements(_scipy_signal.convolve)
def convolve(in1, in2, mode='full', method='auto'):
    return _cupy_signal.convolve(in1, in2, mode=mode, method=method)
convolve.__doc__ = _cupy_signal.convolve.__doc__


@_implements(_scipy_signal.correlate)
def correlate(in1, in2, mode='full', method='auto'):
    return _cupy_signal.correlate(in1, in2, mode=mode, method=method)
correlate.__doc__ = _cupy_signal.correlate.__doc__


@_implements(_scipy_signal.fftconvolve)
def fftconvolve(in1, in2, mode="full", axes=None):
    return _cupy_signal.fftconvolve(in1, in2, mode=mode, axes=axes)
fftconvolve.__doc__ = _cupy_signal.fftconvolve.__doc__


@_implements(_scipy_signal.oaconvolve)
def oaconvolve(in1, in2, mode="full", axes=None):
    return _cupy_signal.oaconvolve(in1, in2, mode=mode, axes=axes)
oaconvolve.__doc__ = _cupy_signal.oaconvolve.__doc__


@_implements(_scipy_signal.convolve2d)
def convolve2d(in1, in2, mode='full', boundary='fill', fillvalue=0):
    return _cupy_signal.convolve2d(in1, in2, mode=mode,
                                   boundary=boundary, fillvalue=fillvalue)
convolve2d.__doc__ = _cupy_signal.convolve2d.__doc__
