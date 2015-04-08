try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='joj',
    version="1.3.0",
    description='Majic Web Application',
    author='Tessella Ltd',
    author_email='majic@ceh.ac.uk',
    url='https://majic.ceh.ac.uk',
    install_requires=[
        "WebOb<=1.3.1",
        "pylons",
        "genshi",
        "SQLAlchemy",
        "repoze.who",
        "mysql-connector-python",
        "numpy",
        "NetCDF4",
        "pydap",
        "coards",
        "FormEncode>=1.3.0a1",
        "PyHamcrest",
        "Mock",
        "Image",
        "matplotlib",
        "libxml2dom",
        "owslib",
        'webhelpers',
        'requests',
        'lxml',
        'f90nml==0.4',
        'pycairo',
        "alembic"],
    tests_require=[
        "PyHamcrest",
        "Mock"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'jules-jasmin': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'cowsclient': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = joj.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    load_endpoints = joj.scripts.load_endpoints:main

    [nose.plugins]
    pylons = pylons.test:PylonsPlugin
    """,
)
