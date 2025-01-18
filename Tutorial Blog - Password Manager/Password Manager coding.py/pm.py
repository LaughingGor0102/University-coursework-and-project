from cryptography.fernet import Fernet
import os
import glob
import random
import string

# a function to clear the terminal screen
def clear():
 
    # detect operating system 
    if os.name == 'nt': #for windows
        _ = os.system('cls')
 
    else:               #for mac and linux
        _ = os.system('clear') 

# a function to generate a random string 
def generate_random_string(len):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(12)])
    
class PasswordManager:

    def __init__(self):
        self.key = None
        self.password_file = None
        self.password_dict = {}

    def print_main_menu(self):
        print("""What do you want to do?
        (1) Create new password file
        (2) Manage existing password file
        (q) Quit
        """)

    def manage_pwFile_menu(self):

        # print all password files
        txtfiles = []
        for file in glob.glob("*.txt"):
            txtfiles.append(file)
        print("Password files you have: ")
        print("\n".join(txtfiles))

        # enter the file to be loaded and prompt the user to input a password for this file
        path = input("Choose a file you want to manage (enter q to exit): ")
        if path == 'q':
            return
        if self.load_password_file(path) == -1:
            return
 
        file_password = input("Enter the password of this file: ")

        while file_password != self.password_dict["file password"]:
            file_password = input("Wrong password! Try again (input q to exit): ")
            if file_password == "q":
                return

        # print menu when password is correct
        done = False

        while done is not True:
            clear()
            print("""What do you want to do?
            (1) Add a password
            (2) View this password file
            (q) Quit
            """)
            choice = input("Enter your choice: ")
            if choice == "1":
                self.add_password()
            elif choice == "2":
                print("\n")
                for key, value in self.password_dict.items():
                    if key == "file password":
                        continue
                    print(key, ' : ', value)
                print("\n")
                input("Click enter to continue")
            elif choice == "q":
                done = True
            else:
                print("Invalid choice!")
        
    def masterPW_is_created(self):
        return os.path.exists("master_password")

    def create_key(self, path):
        self.key = Fernet.generate_key()
        with open(path, 'wb') as f:
            f.write(self.key)

    def load_key(self, path):
        with open(path, 'rb') as f:
            self.key = f.read()

    def create_masterPassword(self, master_password):
        with open("master_password", 'a+') as f:
            f.write(Fernet(self.key).encrypt(master_password.encode()).decode())

    def load_masterPW(self):
        with open("master_password", 'rb') as f:
            encrypted_masterPW = f.read()
            decrypted_masterPW = Fernet(self.key).decrypt(encrypted_masterPW)
            return decrypted_masterPW.decode()

    def create_password_file(self, path, initial_values=None):
        self.password_file = path
        # check if file exist
        if os.path.exists(path):
            input("Password file exist! Press enter to continue")
            return

        # prompt user to create a file password 
        file_password = input("Create a password for this file: ")

        with open(path, 'w') as f:
            encrypted_site = Fernet(self.key).encrypt("file password".encode())
            encrypted_password = Fernet(self.key).encrypt(file_password.encode())
            f.write(encrypted_site.decode() + ":" + encrypted_password.decode() + "\n")
        if initial_values is not None:
            for key, value in initial_values.items():
                self.add_password(key, value)

    def load_password_file(self, path):
        if os.path.exists(path) == False:
            input("Password file not exist. Press enter to continue. ")
            return -1
        self.password_file = path

        #Decrypt every line in the loaded password file, then store it to a dictionary variable
        with open(path, 'r') as f:
            for line in f:
                encrypted_site, encrypted_password = line.split(":")
                decrypted_site = Fernet(self.key).decrypt(encrypted_site.encode().decode()).decode()
                decrypted_password = Fernet(self.key).decrypt(encrypted_password.encode().decode()).decode()
                self.password_dict[decrypted_site] = decrypted_password

    def add_password(self):
        #Error checking: check if a password file is load
        if self.password_file is None:
            print("Load a password file first.")
            return

        #prompt user to input the site and password they want to add
        site = input("Enter the site: ")

        print("""
        1) Enter your password
        2) Generate a password
        q) Quit
        """)

        done = False
        while done is False:
            choice = input("Enter your choice: ")
            if choice == "1":
                password = input("Enter the password: ")
                done = True
            elif choice == "2":
                password = generate_random_string(12)
                done = True
            elif choice == "q":
                return
            else:
                print("Invalid choice!")

        self.password_dict[site] = password

        #add pw to the loaded file
        with open(self.password_file, 'a+') as f:
            encrypted_site = Fernet(self.key).encrypt(site.encode())
            encrypted_password = Fernet(self.key).encrypt(password.encode())
            f.write(encrypted_site.decode() + ":" + encrypted_password.decode() + "\n")
    
    def get_password(self, site):
        return self.password_dict[site]

def main():

    clear()

    #initialize variables
    password = {}   # a dictionary to store the passwords loaded from the key files
    pm = PasswordManager()

    #check/create master password
    if pm.masterPW_is_created() == False:
        pm.create_key("key")
        var = input("Create a master password: ")
        pm.create_masterPassword(var)
    else:
        pm.load_key("key")
        str1 = input("Enter your master password: ")
        while str1 != pm.load_masterPW():
            str1 = input("Wrong master password, try again: ")

    done = False

    #menu choice
    while not done:
        # print(pm.key)
        # print(pm.password_dict)
        # print(pm.password_file)
        clear()
        pm.print_main_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            clear()
            path = input("Create a file name: ")
            pm.create_password_file(path+".txt")
        elif choice == "2":
            clear()
            pm.manage_pwFile_menu()
        elif choice == "q":
            done = True
            print("Bye")
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
