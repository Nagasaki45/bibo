from setuptools import setup

setup(
    name='bibo',
    version='0.0.1',
    py_modules=['bibo'],
    install_requires=[
        'click',
        'pybtex',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        bibo=bibo:cli
    ''',
)
