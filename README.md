# QIB importer

Function: Connect to an XNAT instance. There the script finds the QIB datatypes from XNAT.
These datatypes are than transformed into a directory structure that can be uploaded to TranSMART.


Requirements:
xnatpy      Downloadable here: https://bitbucket.org/bigr_erasmusmc/xnatpy

Parameters:

- connection    Location of the configuration file for establishing XNAT connection.
- params        Location of the configuration file for the variables in the .param files.
- tags          Location of the configuration file for the tags.


Configuration file format:

--connection configuration file:

```
[Connection]
url =
user =
password =
project =

[Directory]
path =
```

--params configuration file:

```
[Study]
STUDY_ID =
SECURITY_REQUIRED =
TOP_NODE =
```

--tags configuration file:

```
[Tags]
Taglist =
```

TODO:
Make the script functional with python3. Right now it returns an error from XNAT.