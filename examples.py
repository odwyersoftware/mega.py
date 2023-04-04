import os
import uuid
from mega import Mega


def test():
    """
    Enter your account details to begin
    comment/uncomment lines to test various parts of the API
    see readme.md for more information
    """
    unique = str(uuid.uuid4())
    # user details
    email = os.environ['EMAIL']
    password = os.environ['PASS']

    mega = Mega()
    # mega = Mega({'verbose': True})  # verbose option for print output

    # login
    m = mega.login(email, password)

    # get user details
    details = m.get_user()
    print(details)

    # get account files
    files = m.get_files()

    # get account disk quota in MB
    print((m.get_quota()))
    # get account storage space
    print((m.get_storage_space()))

    # example iterate over files
    for file in files:
        print((files[file]))

    # upload file
    print((m.upload(filename='examples.py',
                    dest_filename=f'examples_{unique}.py')))

    with open('examples.py', 'rb') as input_file:
        print((m.upload(input_file=input_file, dest_filename='examples.py', file_size=os.path.getsize('examples.py'))))

    # search for a file in account
    file = m.find(f'examples_{unique}.py')

    if file:
        # get public link
        link = m.get_link(file)
        print(link)

        # download file. by file object or url
        print(m.download(file, '/tmp'))
        # m.download_url(link)

        with open(f'/tmp/examples_{unique}.py', 'wb') as output_file:
            print(m.download(file, output_file=output_file))

        # delete or destroy file. by id or url
        print((m.delete(file[0])))
        # print(m.destroy(file[0]))
        # print(m.delete_url(link))
        # print(m.destroy_url(link))

    # empty trash
    print((m.empty_trash()))


if __name__ == '__main__':
    test()
