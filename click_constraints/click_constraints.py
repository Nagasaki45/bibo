import functools

import click


def constrain(constrained, depends=None, conflicts=None):
    '''
    Constrain `constrained` to have all `depends` and non of `conflicts`.
    '''

    if depends is None:
        depends = []
    if conflicts is None:
        conflicts = []

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if kwargs.get(constrained):
                for dependency in depends:
                    if not kwargs.get(dependency):
                        msg = f'{constrained} depends on {dependency}'
                        raise click.BadOptionUsage(constrained, msg)
                for conflicting in conflicts:
                    if kwargs.get(conflicting):
                        msg = f'{constrained} conflicts with {conflicting}'
                        raise click.BadOptionUsage(constrained, msg)
            return f(*args, **kwargs)
        return wrapper
    return decorator
