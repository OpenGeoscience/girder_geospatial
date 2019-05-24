from setuptools import setup

setup(
    name='girder-geospatial-vector',
    author='Kitware, Inc.',
    entry_points={
        'geometa.types': [
            'vector=geometa_vector.schema:handler'
        ]
    },
    packages=[
        'geometa_vector'
    ]
)
