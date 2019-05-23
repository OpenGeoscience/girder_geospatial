from setuptools import setup

setup(
    name='girder-geospatial',
    author='Kitware, Inc.',
    description='Generate metadata for various geospatial datasets',
    version='0.1.0a2',
    packages=[
        'geometa'
    ],
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
