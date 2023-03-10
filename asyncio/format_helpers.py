def _get_function_source(func):
    return None


def _format_callback_source(func, args):
    func_repr = _format_callback(func, args, None)
    source = _get_function_source(func)
    if source:
        func_repr += f' at {source[0]}:{source[1]}'
    return func_repr


def _format_args_and_kwargs(args, kwargs):
    """Format function arguments and keyword arguments.

    Special case for a single parameter: ('hello',) is formatted as ('hello').
    """
    # use reprlib to limit the length of the output
    items = []
    if args:
        items.extend(repr(arg) for arg in args)
    if kwargs:
        items.extend(f'{k}={repr(v)}' for k, v in kwargs.items())
    return '({})'.format(', '.join(items))


def _format_callback(func, args, kwargs, suffix=''):
    # if isinstance(func, functools.partial):
    #     suffix = _format_args_and_kwargs(args, kwargs) + suffix
    #     return _format_callback(func.func, func.args, func.keywords, suffix)

    if hasattr(func, '__qualname__') and func.__qualname__:
        func_repr = func.__qualname__
    elif hasattr(func, '__name__') and func.__name__:
        func_repr = func.__name__
    else:
        func_repr = repr(func)

    func_repr += _format_args_and_kwargs(args, kwargs)
    if suffix:
        func_repr += suffix
    return func_repr


def extract_stack(f=None, limit=None):
    """Replacement for traceback.extract_stack() that only does the
    necessary work for asyncio debug mode.
    """
    return []
