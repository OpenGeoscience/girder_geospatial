from setuptools import setup
import subprocess

system_gdal_version = subprocess.check_output(['gdal-config', '--version'])

setup(
    name='girder-plugin-geometa-vector',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'vector=geometa_vector.schema:handler'
        ]
    },
    packages=[
        'geometa_vector'
    ],
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        # Trying our best with gdal
        'gdal=={}'.format(system_gdal_version)
    ]
)
