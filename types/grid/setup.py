from setuptools import setup


setup(
    name='girder-plugin-geometa-grid',
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
