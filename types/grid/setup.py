from setuptools import setup


setup(
    name='girder-geospatial-grid',
    version='0.1.1',
    description='Support for grid data types'
                'in the girder-geospatial package',
    url='https://github.com/OpenGeoscience/girder_geospatial',
    maintainer='Kitware, Inc.',
    maintainer_email='kitware@kitware.com',
    entry_points={
        'geometa.types': [
            'grid=geometa_grid.schema:handler'
        ]
    },
    packages=[
        'geometa_grid'
    ],
    install_requires=[
        'girder-geospatial'
    ]
)
