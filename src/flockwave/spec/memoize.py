"""This module is based on https://pypi.org/project/memoized/ by George
Sakkis, licensed under the MIT license. It has been modified as follows:

* Dropped support for Python 2.x

* Gotten rid of deprecation errors in Python 3

* Added basic typing information

* Dropped support for signature-preserving decorators to get rid of its
  dependency on the 'decorator' module.
"""

from functools import partial, wraps
from inspect import Parameter, signature
from pickle import dumps
from typing import (
    Any,
    Callable,
    Dict,
    MutableMapping,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

__all__ = ("memoized",)


Arg = TypeVar("Arg")
T = TypeVar("T")

Cache = MutableMapping[Arg, T]


@overload
def memoized(
    func: Callable[[], T],
    is_method: bool = False,
    allow_named: Optional[bool] = None,
    hashable: bool = True,
    cache: Optional[Cache[Any, T]] = None,
) -> Callable[[], T]:
    ...


@overload
def memoized(
    func: Callable[..., T],
    is_method: bool = False,
    allow_named: Optional[bool] = None,
    hashable: bool = True,
    cache: Optional[Cache[Any, T]] = None,
) -> Callable[..., T]:
    ...


@overload
def memoized(
    func: None,
    is_method: bool = False,
    allow_named: Optional[bool] = None,
    hashable: bool = True,
    cache: Optional[Cache[Any, T]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    ...


def memoized(
    func: Optional[Callable[..., T]] = None,
    is_method: bool = False,
    allow_named: Optional[bool] = None,
    hashable: bool = True,
    cache: Optional[Cache[Any, T]] = None,
) -> Union[Callable[..., T], Callable[[Callable[..., T]], Callable[..., T]]]:
    """A generic efficient memoized decorator.

    Creates a memoizing decorator that decorates a function as efficiently as
    possible given the function's signature and the passed options.

    Parameters:
        func: If not None it decorates the given callable ``func``, otherwise
            it returns a decorator. Basically a convenience for creating a
            decorator with the default parameters as ``@memoized`` instead
            of ``@memoized()``.
        is_method: Specify whether the decorated function is going to be a
            method. Currently this is only used as a hint for returning an
            efficient implementation for single argument functions (but not
            methods).
        allow_named: Specify whether the memoized function should allow to be
            called by passing named parameters (e.g. ``f(x=3)`` instead of ``f(3)``).
            For performance reasons this is by default False if the function does
            not have optional parameters and True otherwise.
        hashable: Set to False if any parameter may be non-hashable.
        cache: A dict-like instance to be used as the underlying storage for
            the memoized values. The cache instance must implement
            ``__getitem__`` and ``__setitem__``. Defaults to a new empty dict.
    """
    if func is None:
        return partial(
            memoized,
            is_method=is_method,
            allow_named=allow_named,
            hashable=hashable,
            cache=cache,
        )  # type: ignore

    sig = signature(func)
    has_defaults = any(
        param.default is not Parameter.empty for param in sig.parameters.values()
    )

    if allow_named is None:
        allow_named = has_defaults
    if allow_named or any(
        param.kind is Parameter.VAR_KEYWORD for param in sig.parameters.values()
    ):
        if cache is None:
            cache = {}

        return _args_kwargs_memoized(func, hashable, cache)

    nargs = sum(
        1
        for param in sig.parameters.values()
        if param.kind
        in (
            Parameter.POSITIONAL_ONLY,
            Parameter.POSITIONAL_OR_KEYWORD,
            Parameter.KEYWORD_ONLY,
        )
    )

    if (
        nargs > 1
        or any(
            param.kind is Parameter.VAR_POSITIONAL for param in sig.parameters.values()
        )
        or has_defaults
        or not hashable
        or nargs == 0
        and cache is not None
    ):
        if cache is None:
            cache = {}

        return _args_memoized(func, hashable, cache)

    if nargs == 1:
        if is_method or cache is not None:
            return _one_arg_memoized(func, cache if cache is not None else {})
        else:
            return _fast_one_arg_memoized(func)

    return _fast_zero_arg_memoized(func)


def _args_kwargs_memoized(
    func: Callable[..., T], hashable: bool, cache: Cache[Any, T]
) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if hashable:
            key = (args, frozenset(_iteritems(kwargs)))
        else:
            key = dumps((args, kwargs), -1)
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args, **kwargs)
            return value

    return wrapper


def _args_memoized(
    func: Callable[..., T], hashable: bool, cache: Cache[Any, T]
) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args) -> T:
        key = args if hashable else dumps(args, -1)
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(*args)
            return value

    return wrapper


def _one_arg_memoized(
    func: Callable[[Arg], T], cache: Cache[Arg, T]
) -> Callable[[Arg], T]:
    @wraps(func)
    def wrapper(arg: Arg) -> T:
        key = arg
        try:
            return cache[key]
        except KeyError:
            cache[key] = value = func(arg)
            return value

    return wrapper


# Shamelessly stolen from
# http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def _fast_one_arg_memoized(func: Callable[[Arg], T]) -> Callable[[Arg], T]:
    class memodict(dict):
        def __missing__(self, key: Arg) -> T:
            self[key] = ret = func(key)
            return ret

    cache = cast(Dict[Arg, T], memodict())
    return cache.__getitem__


# same principle as the above
def _fast_zero_arg_memoized(func: Callable[[], T]) -> Callable[[], T]:
    class memodict(dict):
        def __missing__(self, key: Any) -> T:
            self[key] = ret = func()
            return ret

    return partial(memodict().__getitem__, None)


# Taken from future.util
def _iteritems(obj, **kwargs):
    func = getattr(obj, "iteritems", None)
    if not func:
        func = obj.items
    return func(**kwargs)
