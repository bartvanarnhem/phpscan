# PHPScan
PHPScan is a symbolic execution inspired PHP application scanner for code-path discovery. Using a custom extension, it hooks directly into the Zend Engine to track variables and opcodes (assignments, comparisons, etc). Using this information it tries to satisfy as many branch conditions as possible. The goal is to discover valid input (in terms of *$_GET*, *$_POST* and *$_COOKIE* variables and values) that results in reaching a specfic location within the application or to maximize code coverage.

**Author**
Bart van Arnhem (bartvanarnhem@gmail.com).

## Disclaimer
PHPScan is very much a work-in-progress and is not yet in a state to be used on larger real-world applications. If you have any suggestions or feedback please let me know.

## Usage

```
$ python phpscan.py --help
usage: phpscan.py [-h] [-v {0,1,2}] entrypoint

positional arguments:
  entrypoint            the PHP application entrypoint

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1,2}, --verbose {0,1,2}
                        increase verbosity (0 = results only, 1 = show
                        progress, 2 = debug
```

**example** examples/example3.php
```php
<?php
if (isset($_GET['page'], $_GET['num']))
{
  if ($_GET['page'] === 'home')
  {
    phpscan_flag('reached_home');
  }
  
  if (intval($_GET['num'] > 10))
  {
    phpscan_flag('reached_greater_than');
  }
}
?>
```

```
$ python phpscan.py examples/example3.php
Scanning of examples/example3.php finished...
 - Needed 5 runs
 - Took 0.234709 seconds

Successfully reached "reached_home" using input:
_POST
_GET
  num
    value: 11 (integer)
  page
    value: home (string)
_COOKIE
_REQUEST

Successfully reached "reached_greater_than" using input:
_POST
_GET
  num
    value: 11 (integer)
  page
    value: home (string)
_COOKIE
_REQUEST
```

## Installation
### Install dependencies
#### PHP7
```
$ sudo apt-get install php7.1-cli
```
#### Build Runkit7 extension
Build the unofficial PHP7 runkit fork according to the instructions at https://github.com/TysonAndre/runkit7#building-and-installing-runkit7-in-unix

To enable Runkit7 and allow overriding of internal PHP functions add the following lines to your php.ini configuration file:

```
extension=runkit.so
runkit.internal_override=On
```

### Download latest PHPScan
```
$ git clone https://github.com/bartvanarnhem/phpscan.git
```

### Build the Zend Extension

```
$ cd phpscan/zend_extension
$ phpize
$ ./configure
$ make
$ sudo make install
```

To enable the PHPScan Zend Extension add the following lines to your php.ini configuration file: 
```
extension=phpscan.so
```


