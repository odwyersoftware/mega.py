# Mega.py

Python library for the Mega.co.nz API, currently supporting:
 - login
 - uploading
 - downloading
 - deleting
 - searching
 - sharing

This is a work in progress, further functionality coming shortly.

## How To Use

### Create an instance of Mega.py

    mega = Mega()

### Login to Mega

    m = mega.login(email, password)

### Get user details

    details = m.get_user()

### Get account files

    files = m.get_files()

### Upload a file, and get its public link

    file = m.upload('myfile.doc')
    m.get_upload_link(file)

### Download a file from URL or file obj, optionally specify destination folder
    file = m.find('myfile.doc')
    m.download(file)
    m.download_url('https://mega.co.nz/#!utYjgSTQ!OM4U3V5v_W4N5edSo0wolg1D5H0fwSrLD3oLnLuS9pc')
    m.download(file, '/home/john-smith/Desktop')

### Search account for a file, and get its public link
    file = m.find('myfile.doc')
    m.get_link(file)

### Trash a file from URL, it's ID, or from search

    m.delete('utYjgSTQ')
    m.delete_url('https://mega.co.nz/#!utYjgSTQ!OM4U3V5v_W4N5edSo0wolg1D5H0fwSrLD3oLnLuS9pc')

    files = m.find('myfile.doc')
    if files:
        m.delete(files[1]['k'])

## Requirements

    1. Python2.7+
    2. Python requests - python-requests.org
    3. PyCrypto - dlitz.net/software/pycrypto/

## Tests

    Test .py files can be found in /tests, run these to ensure Mega.py is working 100%.

## Contribute

    Feel free to pull the source and make changes and additions.

    Learn about the API at Mega.co.nz, more documentation coming shortly.
    - https://mega.co.nz/#developers



Thanks to http://julien-marchand.com/blog/contact for examples


