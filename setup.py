try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='ecomaps',
    version="1.7.0", 
    #description='',
    #author='',
    #author_email='',
    #url='',
    install_requires=["Pylons==1.0", "genshi"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'ecomaps['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'cowsclient': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = ecomaps.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [console_scripts]
    load_endpoints = ecomaps.scripts.load_endpoints:main
    """,
)
