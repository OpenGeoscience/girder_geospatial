from setuptools import setup

setup(
    name='girder-plugin-geometa-raster',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'raster=geometa_raster.schema:handler'
        ]
    },
    packages=[
        'geometa_raster'
    ],
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        'gdal'
    ]
)
