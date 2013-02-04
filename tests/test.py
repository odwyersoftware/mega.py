from mega import Mega

def test():
    #user details
    email = 'your@email.com'
    password = 'password'

    mega = Mega()

    #login
    m =  mega.login(email, password)

    #get user details
    details = m.get_user()
    print(details)

    #get account files
    files = m.get_files()
    print(files)

    #upload file
    print(m.upload('test.py'))

    #trash a file, by id or url
    #print(m.delete('C5pxAbr'))
    #print(m.delete_url('https://mega.co.nz/#!C5pxAbrL!SPxZH0Ovn2DLK_n5hLlkGQ2oTD8HcU6TYiz_TPg78kY'))

    #download file from url
    m.download_url('https://mega.co.nz/#!6hBW0R4a!By7-Vjj5xal8K5w_IXH3PlGNyZ1VvIrjZkOmHGq1X00')

if __name__ == '__main__':
    test()