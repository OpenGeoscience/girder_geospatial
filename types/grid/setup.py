from setuptools import setup


setup(
    name='girder-plugin-geometa-grid',
    author='Kitware, Inc.',
    entry_points={
        'geometa.formats': [
            'grid=geometa_grid.schema:handler'
        ]
    },
    packages=[
        'geometa_grid'
    ],
    install_requires=[
        # Eventually will require geometa girder plugin
        # as a dependency here
        'gdal'
    ]
)
