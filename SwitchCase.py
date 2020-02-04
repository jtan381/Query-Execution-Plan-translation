import re

class Switcher:
    def case (self, type, qry):
        method_name = type.replace(" ", "")
        method = getattr(self, method_name, lambda: 'Invalid')
        return method(qry)

    def HashCond (self,qry):
        return self.JoinsType(qry)

    def RecheckCond (self,qry):
        return 'RecheckCond: '+qry

    def SortKey (self,qry):
        count = 0
        string = ''
        for sortKey in qry:
            if count == 0:
                string = str(sortKey)
                count += 1
            elif count > 0:
                string += ' and ' + str(sortKey)
        return string

    def GroupKey (self,qry):
        count = 0
        string = ''
        for sortKey in qry:
            if count == 0:
                string = str(sortKey)
                count += 1
            elif count > 0:
                string += ' and ' + str(sortKey)
        print(string)
        return string

    def TableFilter (self,qry):
        return self.JoinsType(qry)

    def JoinFilter (self,qry):
        return self.JoinsType(qry)
        # previous working code below...
        # str_list = list(filter(None, qry.split()))
        # #print(str_list)
        # string = ''
        # for word in str_list:
        #     newWord = (re.split(r'[`\-~!@#$%^&*()+\[\]{};\'\\"|,./?]|::', word))
        #     newWord = list(filter(None, newWord))
        #     newWord = str(newWord[0])
        #     string += newWord
        # return (" ".join(string))

    def JoinsType(self, qry):
        str_list = list(filter(None, qry.split()))
        #print(qry)
        #print(str_list)
        string = ''
        #print(str_list)
        for word in str_list:
            newWord = (re.split(r'[()\[\]{};\'"/]|::', word))
            #print('1.',newWord)
            newWord = list(filter(None, newWord))
            #print('2.',newWord)
            #print(newWord)
            if len(newWord) == 1:
                newWord[0] = newWord[0].split('.')
                #print(newWord)
                if len(newWord[0]) == 1:
                    newWord = str(newWord[0][0])
                elif len(newWord[0]) == 2:
                    newWord = str(newWord[0][1])

            elif len(newWord) == 2:
                newWord[1] = newWord[1].split('.')
                if len(newWord[1]) == 1:
                    newWord[1] = newWord[1][0]
                elif len(newWord[1]) == 2:
                    newWord[1] = newWord[1][1]
                newWord = str(newWord[0]) + '(' + str(newWord[1]) + ')'
            #print('3.',newWord)
            #print(newWord)
            string += newWord + ' '
        return (string)
