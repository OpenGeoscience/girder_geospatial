from setuptools import setup

setup(
    name='girder-plugin-geometa-geotiff',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'geotiff=schema'
        ]
    }
)
