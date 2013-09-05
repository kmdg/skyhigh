from setuptools import setup, find_packages

setup(
    name='skyhigh',
    version='0.1.0',
    description='Skyhigh Networks Website',
    author='Unomena Developers',
    author_email='dev@unomena.com',
    url='http://unomena.com',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    dependency_links = [
        'http://github.com/unomena/django-photologue/tarball/2.8.praekelt#egg=django-photologue-2.8.praekelt',
        'http://github.com/unomena/unobase/tarball/0.1.2#egg=unobase-0.1.2',
    ],
    install_requires = [
        'django-evolution',
        'django-ckeditor==3.6.2.1',
        'django-photologue==2.8.praekelt',
        'django-registration==0.8',
        'django-preferences',
        'python-memcached',
        'psycopg2',
        'mysql-python',
        'gunicorn',
        'flufl.password',
        'flup',
        'pytz',
        'Pillow',
        'suds==0.3.9',
        'pycurl',
        'celery',
        'django-celery',
        'salesforce-python-toolkit',
        'django-honeypot',
        'unobase==0.1.2'
    ],
    include_package_data=True,
)
