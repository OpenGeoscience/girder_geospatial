from setuptools import setup

setup(
    name='girder-geospatial-vector',
    version='0.1.1',
    description='Support for vector data types'
                'in the girder-geospatial package',
    url='https://github.com/OpenGeoscience/girder_geospatial',
    maintainer='Kitware, Inc.',
    maintainer_email='kitware@kitware.com',
    entry_points={
        'geometa.types': [
            'vector=geometa_vector.schema:handler'
        ]
    },
    packages=[
        'geometa_vector'
    ],
    install_requires=[
        'girder-geospatial'
    ]
)
