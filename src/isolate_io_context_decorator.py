"""An I/O context isolation decorator.

This decorators isolates I/O context of target
function or method from phpsploit.

I/O Context is a mix of terminal related elements,
such as current stdout and readline completer
attributes.

This decorator is useful if you run something
that reconfigures the readline completer, or
needs to use the default stdout file descriptor
instead of the phpsploit's stdout wrapper.

"""

import sys


# currently supported I/O entities
IO_ENTITIES = ["readline", "stdout"]


def init_decorator_args(kwargs):
    # enable all by default is no arguments provided
    if not kwargs:
        return dict.fromkeys(IO_ENTITIES, True)
    # set IO_ENTITIES values
    arguments = {}
    for key, value in kwargs.items():
        if key not in IO_ENTITIES:
            raise TypeError("invalid io entity: %r" % key)
        elif not isinstance(value, bool):
            raise TypeError("%s=%r: boolean expected" % (key, value))
        else:
            arguments[key] = value
    # ensure a value is provided for ALL entities.
    if set(arguments.keys()) != set(IO_ENTITIES):
        raise ValueError("all IO_ENTITIES must be explicitly provided")
    return arguments


def isolate_io_context(**decorator_kwargs):
    """Isolate I/O context.

    If no arguments are given, all IO_ENTITIES are set to True.
    Otherwise, each entity must be passed as argument with the
    wanted boolean value, for enabling or disabling them.

    Valid usage examples:
    >>> @isolate_io_context() # enable all
    >>> @isolate_io_context(readline=True, stdout=False) # only enable readline

    Invalid usage example:
    >>> @isolate_io_context(stdout=False) # readline value not explicitly given

    """
    decorator_args = init_decorator_args(decorator_kwargs)

    def decorator(function):
        def wrapper(*args, **kwargs):
            # if unavailable, disable readline backup silently
            if decorator_args["readline"]:
                try:
                    import readline
                except:
                    decorator_args["readline"] = False
            # backup I/O Entities
            if decorator_args["readline"]:
                old_readline_completer = readline.get_completer()
                readline.set_completer((lambda x: x))
            if decorator_args["stdout"]:
                old_stdout = sys.stdout
                sys.stdout = sys.__stdout__
            # execute function with fresh context
            try:
                retval = function(*args, **kwargs)
            # restore I/O Entities
            finally:
                if decorator_args["readline"]:
                    readline.set_completer(old_readline_completer)
                if decorator_args["stdout"]:
                    sys.stdout = old_stdout
            return retval

        return wrapper

    return decorator
