from setuptools import setup

setup(
    name='girder-geospatial-raster',
    version='0.1.1',
    description='Support for raster data types'
                'in the girder-geospatial package',
    url='https://github.com/OpenGeoscience/girder_geospatial',
    maintainer='Kitware, Inc.',
    maintainer_email='kitware@kitware.com',
    entry_points={
        'geometa.types': [
            'raster=geometa_raster.schema:handler'
        ]
    },
    packages=[
        'geometa_raster'
    ],
    install_requires=[
        'girder-geospatial'
    ]
)
