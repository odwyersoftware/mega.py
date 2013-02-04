# Mega.py

Python library for the Mega.co.nz API, currently supporting login, uploading & downloading of files.

This is a work in progress, further functionality coming shortly.

## How To Use

### Create an instance of Mega.py

    mega = Mega()

### Login to Mega

    m = mega.login(email, password)

### Get account files

    files = m.get_files()

### Upload a file

    m.upload('myfile.doc')

### Download a file from URL

    m.download_url('https://mega.co.nz/#!utYjgSTQ!OM4U3V5v_W4N5edSo0wolg1D5H0fwSrLD3oLnLuS9pc')


## Requirements

    1. Python2.7+
    2. Python requests - python-requests.org

## Tests

    Test .py files can be found in /tests, run these to ensure Mega.py is working 100%.

## Contribute

    Feel free to pull the source and make changes and additions.

    Learn about the API at Mega.co.nz
    - https://mega.co.nz/#developers


