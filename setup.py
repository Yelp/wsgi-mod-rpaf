from setuptools import setup

setup(
    name='wsgi-mod-rpaf',
    description='WSGI middleware implementing apache mod-rpaf',
    url='https://github.com/Yelp/wsgi-mod-rpaf',
    version='3.0.0',
    author='Anthony Sottile',
    author_email='asottile@umich.edu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    py_modules=['wsgi_mod_rpaf'],
    install_requires=['six'],
    extras_require={':python_version=="2.7"': ['ipaddress']},
)
