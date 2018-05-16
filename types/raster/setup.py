from setuptools import setup
import subprocess

system_gdal_version = subprocess.check_output(['gdal-config', '--version'])

setup(
    name='girder-plugin-geometa-raster',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'raster=schema'
        ]
    },
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        # Trying our best with gdal
        'gdal=={}'.format(system_gdal_version)
    ]
)
