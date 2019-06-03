from setuptools import setup, find_packages

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='girder-geospatial',
    version='0.2.0',
    description='Generate metadata for various geospatial datasets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OpenGeoscience/girder_geospatial',
    maintainer='Kitware, Inc.',
    maintainer_email='kitware@kitware.com',
    packages=find_packages(exclude=('tests')),
    entry_points={
        'geometa.types': [],
        'girder.plugin': [
            'geometa = geometa:GeometaPlugin'
        ]
    },
    install_requires=[
        'pyproj',
        'shapely',
        # Will fix it once marshmallow publishes new version
        'marshmallow==3.0.0b10',
        'geojson',
        'rasterio',
        'gdal'
    ],
)
