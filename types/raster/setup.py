from setuptools import setup

setup(
    name='girder-plugin-geometa-raster',
    author='Kitware, Inc.',
    entry_points={
        'geometa.types': [
            'raster=geometa_raster.schema:handler'
        ]
    },
    packages=[
        'geometa_raster'
    ]
)
