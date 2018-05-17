from setuptools import setup

setup(
    name='girder-plugin-geometa',
    author='Kitware, Inc.',
    packages=[
        'geometa'
    ],
    entry_points={
        'geometa.formats': []
    },
    install_requires=[
        'pyproj',
        'shapely',
        # Will fix it once marshmallow publishes new version
        'marshmallow==3.0.0b10',
        'geojson'
    ]
)
