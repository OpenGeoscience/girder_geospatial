from setuptools import setup

setup(
    name='girder-plugin-geometa-vector',
    author='Kitware, Inc.',
    entry_points={
        'geometa.types': [
            'vector=geometa_vector.schema:handler'
        ]
    },
    packages=[
        'geometa_vector'
    ],
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        'gdal'
    ]
)
