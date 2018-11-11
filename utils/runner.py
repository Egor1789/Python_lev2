from subprocess import Popen, CREATE_NEW_CONSOLE

if __name__ == '__main__':
    Popen('python ../server.py', creationflags=CREATE_NEW_CONSOLE)
    Popen('python ../client.py --login pak --password 1', creationflags=CREATE_NEW_CONSOLE)
    Popen('python ../client.py --login andrey --password 1', creationflags=CREATE_NEW_CONSOLE)
