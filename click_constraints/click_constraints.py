import functools

import click


def constrain(constrained, depends=None, conflicts=None):
    """
    Constrain `constrained` to have all `depends` and non of `conflicts`.
    """

    if depends is None:
        depends = []
    if conflicts is None:
        conflicts = []

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if kwargs.get(constrained):
                for d in depends:
                    if not kwargs.get(d):
                        msg = "{} depends on {}".format(constrained, d)
                        raise click.BadOptionUsage(constrained, msg)
                for c in conflicts:
                    if kwargs.get(c):
                        msg = "{} conflicts with {}".format(constrained, c)
                        raise click.BadOptionUsage(constrained, msg)
            return f(*args, **kwargs)

        return wrapper

    return decorator
