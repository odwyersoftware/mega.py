from mega import Mega

def test():
    #user details
    email = 'your@email.com'
    password = 'password'

    mega = Mega()

    ##login
    m = mega.login(email, password)

    ##get user details
    details = m.get_user()
    print(details)

    ##get account files
    files = m.get_files()
    #example iterate over files
    for file in files:
        print files[file]

    ##upload file
    print(m.upload('tests.py'))

    ##get file's public link
    #NOTE: if passing upload() function response use get_upload_link()
    file = m.find('tests.py')
    #print(m.get_upload_link(file))
    print(m.get_link(file))

    ##trash a file, by id or url
    #print(m.delete('f14U0JhD'))
    #print(m.delete_url('https://mega.co.nz/#!f14U0JhD!S_2k-EvB5U1N3s0vm3I5C0JN2toHSGkVf0UxQsiKZ8A'))

    ##search for a file in account
    file = m.find('somefile.doc')
    if file:
        #trash a file by it's id
        print(m.delete(file[1]['k']))

    ##download file
    #file = m.find('tests.py')
    #m.download(file)
    ##specify destination folder
    #m.download(file, '/home/user_name/Desktop')
        #m.download_url('https://mega.co.nz/#!6hBW0R4a!By7-Vjj5xal8K5w_IXH3PlGNyZ1VvIrjZkOmHGq1X00')


if __name__ == '__main__':
    test()