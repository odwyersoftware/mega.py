from mega import Mega

def test():
    #user details
    email = 'your@email.com'
    password = 'password'

    mega = Mega()

    #login
    m = mega.login(email, password)

    #get user details
    details = m.get_user()
    print(details)

    #get account files
    files = m.get_files()

    #example iterate over files
    for file in files:
        print(files[file])

    #upload file
    print(m.upload('tests.py'))

    #search for a file in account
    file = m.find('tests.py')

    if file:
        #get public link
        link = m.get_link(file)
        print(link)

        #download file. by file object or url
        m.download(file, '/tmp')
        #m.download_url(link)

        #delete or destroy file. by id or url
        print(m.delete(file[1]['k']))
        #print(m.destroy(file[1]['h']))
        #print(m.delete_url(link))
        #print(m.destroy_url(link))

    #empty trash
    print(m.empty_trash())

if __name__ == '__main__':
    test()