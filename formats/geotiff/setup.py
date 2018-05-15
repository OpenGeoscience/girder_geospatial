from setuptools import setup

setup(
    name='girder-plugin-geometa-geotiff',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'geotiff=schema'
        ]
    },
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        'rasterio'
    ]
)
