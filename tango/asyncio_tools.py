"""Backport some asyncio features."""

import collections
import concurrent.futures
import functools
import inspect
import types

try:
    import asyncio
except ImportError:
    import trollius as asyncio

__all__ = ("run_coroutine_threadsafe",)


def _set_concurrent_future_state(concurrent, source):
    """Copy state from a future to a concurrent.futures.Future."""
    assert source.done()
    if source.cancelled():
        concurrent.cancel()
    if not concurrent.set_running_or_notify_cancel():
        return
    exception = source.exception()
    if exception is not None:
        concurrent.set_exception(exception)
    else:
        result = source.result()
        concurrent.set_result(result)


def _copy_future_state(source, dest):
    """Internal helper to copy state from another Future.
    The other Future may be a concurrent.futures.Future.
    """
    assert source.done()
    if dest.cancelled():
        return
    assert not dest.done()
    if source.cancelled():
        dest.cancel()
    else:
        exception = source.exception()
        if exception is not None:
            dest.set_exception(exception)
        else:
            result = source.result()
            dest.set_result(result)


def _chain_future(source, dest):
    """Chain two futures so that when one completes, so does the other.
    The result (or exception) of source will be copied to destination.
    If destination is cancelled, source gets cancelled too.
    Compatible with both asyncio.Future and concurrent.futures.Future.
    """
    if not isinstance(source, (asyncio.Future, concurrent.futures.Future)):
        raise TypeError("A future is required for source argument")
    if not isinstance(dest, (asyncio.Future, concurrent.futures.Future)):
        raise TypeError("A future is required for destination argument")
    source_loop = source._loop if isinstance(source, asyncio.Future) else None
    dest_loop = dest._loop if isinstance(dest, asyncio.Future) else None

    def _set_state(future, other):
        if isinstance(future, asyncio.Future):
            _copy_future_state(other, future)
        else:
            _set_concurrent_future_state(future, other)

    def _call_check_cancel(destination):
        if destination.cancelled():
            if source_loop is None or source_loop is dest_loop:
                source.cancel()
            else:
                source_loop.call_soon_threadsafe(source.cancel)

    def _call_set_state(source):
        if dest_loop is None or dest_loop is source_loop:
            _set_state(dest, source)
        else:
            dest_loop.call_soon_threadsafe(_set_state, dest, source)

    dest.add_done_callback(_call_check_cancel)
    source.add_done_callback(_call_set_state)


def run_coroutine_threadsafe(coro, loop):
    """Submit a coroutine object to a given event loop.
    Return a concurrent.futures.Future to access the result.
    """
    if not asyncio.iscoroutine(coro):
        raise TypeError("A coroutine object is required")
    future = concurrent.futures.Future()

    def callback():
        try:
            _chain_future(asyncio.ensure_future(coro, loop=loop), future)
        except Exception as exc:
            if future.set_running_or_notify_cancel():
                future.set_exception(exc)
            raise

    loop.call_soon_threadsafe(callback)
    return future


# Function removed from Python 3.11
# Taken from https://github.com/python/cpython/blob/3.10/Lib/asyncio/coroutines.py
# (without the _DEBUG part)
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022 Python Software Foundation;
# All Rights Reserved
def coroutine(func):
    """Decorator to mark coroutines.
    If the coroutine is not yielded from before it is destroyed,
    an error message is logged.
    """
    if inspect.iscoroutinefunction(func):
        return func

    if inspect.isgeneratorfunction(func):
        coro = func
    else:

        @functools.wraps(func)
        def coro(*args, **kw):
            res = func(*args, **kw)
            if asyncio.isfuture(res) or inspect.isgenerator(res):
                res = yield from res
            else:
                # If 'res' is an awaitable, run it.
                try:
                    await_meth = res.__await__
                except AttributeError:
                    pass
                else:
                    if isinstance(res, collections.abc.Awaitable):
                        res = yield from await_meth()
            return res

    coro = types.coroutine(coro)
    wrapper = coro
    wrapper._is_coroutine = (
        asyncio.coroutines._is_coroutine
    )  # For iscoroutinefunction().
    return wrapper
