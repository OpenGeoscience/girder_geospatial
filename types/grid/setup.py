from setuptools import setup


setup(
    name='girder-geospatial-grid',
    author='Kitware, Inc.',
    entry_points={
        'geometa.types': [
            'grid=geometa_grid.schema:handler'
        ]
    },
    packages=[
        'geometa_grid'
    ]
)
