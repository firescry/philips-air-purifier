# philips-air-purifier
Python module to connect with Philips air purifiers

It is based on [py-air-control](https://github.com/rgerganov/py-air-control) command line tool.

## Device compatibility
Module works with following Philips devices:
* 2000i Series
  * AC2729

## Supported features
Following features are currently supported:
* device discovery in local network (purifier must be already connected to WiFi)
* device control:
  * turn purifier on/off
  * lock/unlock control panel
  * read temperature/humidity/PM2.5/allergen index
  * enable/disable humidifier
  * set auto mode or fan speed
  * set desired humidity and light brightness
  * set a timer and read its status
  * turn display on/off
  * set information presented on display (allergen index/PM2.5/humidity)

## Installation
Module is not available on pypi.org but may be installed with following pip command:
```
$ pip install git+https://github.com/firescry/philips-air-purifier.git#egg=philips_air_purifier
```
