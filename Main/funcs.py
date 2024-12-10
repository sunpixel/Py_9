'''Base functions fro program'''

from random import randint
import Main.data_classes as dc

def string_generator(dl = 16):
    '''Generates a unique username of a random length'''

    def generate(length, lis):
        '''Generates string'''
        string = ''
        while length > 0:
            string += lis[randint(0, len(lis) - 1)]
            length -= 1
        return string

    alph = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    nums = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    spec = ['!', '#', '$', '&', '%']

    n_len = randint(5, dl)  # length of the username

    symb_a = randint(0, n_len)
    symb_n = randint(0, n_len - symb_a)
    symb_s = randint(0, n_len - symb_n)

    return generate(symb_a, alph) + generate(symb_n, nums) + generate(symb_s, spec)



def check_availiability(name, db):
    '''Checks if the username is available'''
    if db.query(dc.User).filter(dc.User.username == name).first():
        return False
    return True
