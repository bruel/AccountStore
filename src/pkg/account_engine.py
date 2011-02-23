# -*- coding: utf-8 -*-
import re
import sys  # Only used for sys.exit() when doing debugging

################ class #################
class Account:
    ''' This class defines an account '''
    def __init__(self, act_fields):  # act_fields is a tuple with the 3 fields
        self.name  = act_fields[0]   # name is "key" i.e. uniqueness required & 
        self.uname = act_fields[1]   # sustained
        self.pword = act_fields[2]
        
    def __str__(self):
        ''' This "to-string" method makes a comma separated line of an account.
        The string also serves as a primitive DTO via AccountManager.csv2list() '''
        return self.name + ', ' + self.uname + ', ' + self.pword

############### class ##################
class AccountManager:
    '''
    This class stores a list of accounts ('accounts') and has various CRUD 
    methods for an account in relation to this list. It of course depends on 
    the preceding Account class
    '''
    def __init__(self):
        ''' When an account AccountManager is created populate 'accounts' list '''
        self.disc2obj()
    
    def disc2obj(self):
        ''' Load the accounts from file. UC "Show All Accounts" '''
        self.accounts = []  # List of accounts. Be sure it's empty
        f = None
        try:
            f = open(File.ACCOUNT_FILE, 'r')
            act_fields = []  # List of the 3 fields of an account
            for line in f:  # line is a account-field
                act_fields.append(line.strip())  # strip(): remove trailing \n
                # When 3 (File.LIN...) lines are read make an account and add it
                if len(act_fields) == File.LINES_PER_ACCOUNT:
                    self.accounts.append(Account(act_fields))
                    act_fields = []  # Reset before reading next account
        except IOError as io:
            print str(io)
        finally:
            if f:
                f.close()  # We don't forget this one do we?
                
    def persist(self, liststore):
        ''' Save the accounts to file '''
        self.gui2obj(liststore)
        # Now the gui's liststore has stored in 'accounts'
        f = None
        try:
            f = open(File.ACCOUNT_FILE, 'w')  # We overwrite any previous content
            for act in self.accounts:         # - backup in case writing f***'s up?
                act_fields = self.csv2list(str(act))  # 'x, y, z' --> ['x', 'y', 'z']
                # next line: ['x', 'y', 'z'] --> ['x\n', 'y\n', 'z\n']
                act_fields = map(lambda s: s + '\n', act_fields) 
                map(f.write, act_fields)  # write all act_fields - the 'map' way :)
        except IOError as io:
            print str(io)
        finally:
            if f:
                f.close()
                
    def gui2obj(self, liststore):
        ''' Helper for persist(): From gui strings to account objects '''
        self.accounts = []
        for row in liststore:  # row is a TreeModelRow
            act = Account([val for val in row])  # Unpacking the TreeModelRow
            self.accounts.append(act)
        self.sort()  # 'accounts' sorted => accounts on file sorted (nice when loading)
    
    def uniq_violation(self, name):
        ''' Helper method for add() '''
        for act in self.accounts:
            if act.name == name:
                raise self.UniquenessException(name)
    

     
    def sort(self):
        ''' In-place sorting of the accounts using 'key'ed-sorting' stolen from
        http://wiki.python.org/moin/HowTo/Sorting/ search 'Key Functions'. Over-
        riding builtin 'cmp' makes sorting case indifferent. Noticeable client 
        is self.add() '''
        self.accounts.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()),
                           key=lambda act: act.name)
    
    def csv2list(self, str):
        ''' helper method - also used in account_store.py (csv: comma separated
        values). Does this: 'x, y, z' --> ['x', 'y', 'z']. It's a neat hack of 
        using a to-string method of an account to get a list of the fields '''
        return re.split(', ', str)
    
    def __str__(self):
        ''' Output the accounts as "a, b, c\nd, e, f\n etc..." '''
        s = '' 
        for act in self.accounts:  # TODO Consider using reduce()
            s += str(act) + '\n'
        return s  
            
    class UniquenessException(Exception):
        def __init__(self, name):
            self.message =  'The account name ' + name + ' is not unique ' + \
                            'among existing account names'
        def __str__(self):
            return self.message
   
    ################### methods not used sofar ###################
    def update(self, name):
        ''' Not implemented yet '''
        pass
    
    def add(self, act):
        ''' Adds an account to the accounts list. And it does it by 1) preserving 
        uniqueness of the names of the accounts (i.e. two accounts having the 
        same name can not be found in the accounts list). 2) The accounts list 
        is sorted after each insert implying thats it's always sorted (the 
        delete operation can't destroy a valid order) '''
        try:
            self.uniq_violation(act.name)
        except self.UniquenessException as ue:
            print str(ue)
        else:    
            self.accounts.append(act)
            self.sort()
            
    def delete(self, name):
        ''' A check for if name *is* in the list of accounts. The check is not 
        really nessessary - the filter-command alone suffices. But it demos 
        map() and filter() which might impress NIR... :D . Joke aside: One 
        could rethrow KeyError so a warning could pop up. But then again: it 
        *can* never happen in this app because the gui will select a 
        line/account which *exists* '''
        try:
            names = map(lambda act: act.name, self.accounts)
            if name not in names:
                raise KeyError('There is no such account name (%s)!' %name)
        except KeyError as ke:
            print str(ke)
        else:   # Well 'name' was there... . filter() *preserves* the elements 
                # that comply to the criteria in the function. Here we want the
                # names not equal to 'name'
            self.accounts = filter(lambda act: act.name != name, self.accounts)

############### class ##################
class File:
    ''' This class contains various file handling constants and also attributes/ 
    methods assisting the file encryption (TODO) '''
    # The AccountManager class knows where to persist it's accounts
    ACCOUNT_FILE = '/usr/lib/gedit-2/plugins/account_store.txt'
    LINES_PER_ACCOUNT = 3

##################### indepent run/test from command line ######################
if __name__ == "__main__":
    am = AccountManager()
    
    am.disc2obj()
    print str(am)
    
    am.delete('KNord')
    print str(am)
    
    act = Account('American Pizza', '60760024', 'n/a')
    am.add(act)
    print str(am)
    
    # Persist, load and confirm correct
    am.persist()
    print 'Efter persist()'
    am.disc2obj()
    print 'Efter disc2obj()'
    
    print str(am)
