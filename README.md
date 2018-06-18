# girder_geospatial
[![CircleCI](https://circleci.com/gh/OpenGeoscience/girder_geospatial/tree/master.svg?style=svg)](https://circleci.com/gh/OpenGeoscience/girder_geospatial/tree/master)
[![codecov](https://codecov.io/gh/OpenGeoscience/girder_geospatial/branch/master/graph/badge.svg)](https://codecov.io/gh/OpenGeoscience/girder_geospatial)

## Installation
1. First step is to [Install girder](https://girder.readthedocs.io/en/latest/installation.html).
2. Install [gdal](http://www.gdal.org/) >= 2 to the system.
3. After that you should be able to:
```sh
pip install gdal
python -c "import gdal"
```
without any errors.

4. Clone girder_geospatial repository. One important thing to note here is the naming conventions. Plugin name should be **geometa**. This extra requirement will go away once girder plugins are pip installable.
```sh
git clone https://github.com/OpenGeoscience/girder_geospatial.git geometa
```
5. Install girder_geospatial plugin.
```sh
girder-install plugin geometa -s
```
6. Enable girder cache by adding following to your [girder config file](https://girder.readthedocs.io/en/latest/configuration.html):
```sh
[cache]
enabled = True
cache.global.backend = "dogpile.cache.memory"
cache.request.backend = "cherrypy_request"
```
8. Install geospatial types
```sh
cd geometa
pip install types/raster/ types/vector/ types/grid/
```
## Running tests
```sh
cd geometa
pip install -r requirements-dev.txt
pytest -n 4
```
