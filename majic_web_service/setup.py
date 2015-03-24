try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='majic_web_service',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "WebOb<=1.3.1",
        "Pylons>=1.0.1rc1",
        "SQLAlchemy>=0.5",
        "mysql-connector-python",
        'pytz'
    ],
    tests_require=[
        "PyHamcrest",
        "Mock"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'majic_web_service': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'majic_web_service': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = majic_web_service.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [nose.plugins]
    pylons = pylons.test:PylonsPlugin
    """,
)
