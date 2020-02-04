"""
Provide a unified interface to a set of interfaces in a subsystem.
Facade defines a higher-level interface that makes the subsystem easier
to use.
"""
from GUI import *
from Login import *
from PostgreSQLComm import *

class Facade:
    """
    Know which subsystem classes are responsible for a request.
    Delegate client requests to appropriate subsystem objects.
    """
    def __init__(self):
        self.loginMenu = loginMenu()
        self.App = App()
        self.status = True
        self.comm = init_comm()
    
    def restart(self):
        self.loginMenu = loginMenu()
        self.App = App()
        self.status = True
        self.comm = init_comm()
        
    def operation(self):
        while(self.status):
            self.restart()
            self.status, self.tableName, self.attr = self.loginMenu.main_login_screen(self.comm)
            if(self.status):
                self.status = self.App.GUI_main(self.tableName, self.attr, self.comm)
            self.comm.CloseConnection()
            print("stop")

def main():
    facade = Facade()
    facade.operation()

if __name__ == "__main__":
    main()
