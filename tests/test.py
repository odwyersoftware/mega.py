from mega import Mega

def test():
    #user details
    email = 'your@email.com'
    password = 'password'

    mega = Mega()

    #login
    m =  mega.login(email, password)

    #get account files
    files = m.get_files()
    print(files)

    #upload file
    print(m.upload('tests/test.py'))

    #download file from url
    m.download_url('https://mega.co.nz/#!utYjgSTQ!OM4U3V5v_W4N5edSo0wolg1D5H0fwSrLD3oLnLuS9pc')

if __name__ == '__main__':
    test()