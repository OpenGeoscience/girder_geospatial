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

## Usage
1. **Uploading a geospatial file**

    After the plugin is enabled in Girder, simply upload a geospatial file that gdal or ogr can handle.
    To see lists of supported formats see [gdal](http://www.gdal.org/formats_list.html) and                        [ogr](http://www.gdal.org/ogr_formats.html) format documentation.
    This plugin will hook into the [upload file](https://github.com/OpenGeoscience/girder_geospatial/blob/master/server/__init__.py#L16-L17) event. File upload will trigger a function which will set geospatial metadata on the uploaded file's item.

2. **Creating geospatial metadata on an already existing item**

    Let's say you already have data in Girder you don't want to reupload your data. There is an
    endpoint which takes an item id and creates geospatial metadata on the item.
    ```sh
    curl '{girderApiUrl}/item/{itemId}/geometa' -X PUT
    ```
    This endpoint will attach 'geometa' key to the given item.

3. **Creating arbitrary geospatial metadata on an existing item**

    Some users might want more control on what they are saving. The same endpoint in option 2 can be used
    to create arbitrary metadata which must follow the [base schema](https://github.com/OpenGeoscience/girder_geospatial/blob/master/geometa/schema/base.py#L29-L48).
    In other words as long as you have the required parameters that are defined in the base
    schema you are free to add your own additional data for your own purposes.
    ```sh
    curl '{girderApiUrl}/item/{itemId}/geometa?geometa={geospatialMetadata}' -X PUT
    ```

4. **Querying mongo for geospatial datasets**

	In order to query mongo use the following endpoint with required query parameters.
	```sh
	curl '{girderApiUrl}/item/geometa?{necessaryQueryStringParameters} -X GET
	```

	You have bunch of options such as providing:
	1. WKT geometry and relation
	2. Bounding box and relation
	3. Geojson geometry and relation
	4. Latitude, longitude and radius.

	When providing latitude, longitude and radius, relation will be always "within" as opposed to
	"intersects" .This might create confusing results. Recommended way of search is using 1, 2 or 3
	above.

	Also, please note these options are mutually exclusive so you cannot pass both geojson and bounding
	box options. [Opensearch Geo Schema validators](https://github.com/OpenGeoscience/girder_geospatial/blob/add-endpoint-documentation/geometa/schema/opensearchgeo.py#L61-L147) will raise an exception if mutually exclusive
	parameters are passed.

5. **Getting geometa from an item**

   In order to get geometa for an item simply hit the following endpoint:
   ```sh
   curl '{girderApiUrl}/item/{itemId}/geometa' -X GET
   ```

## Vagrant Examples
There are currently [2 vagrant examples](https://github.com/OpenGeoscience/girder_geospatial/tree/master/devops/ansible/examples) to quickly get up and running.
If you are having problems installing this plugin check ansible playbooks for
[ubuntu-16.04](https://github.com/OpenGeoscience/girder_geospatial/blob/master/devops/ansible/examples/ubuntu-16.04/playbook.yml) and
[ubuntu-18.04](https://github.com/OpenGeoscience/girder_geospatial/blob/master/devops/ansible/examples/ubuntu-18.04/playbook.yml).

## Running tests
```sh
cd geometa
pip install -r requirements-dev.txt
pytest -n 4
```
