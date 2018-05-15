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
        'pyproj'
    ]
)
