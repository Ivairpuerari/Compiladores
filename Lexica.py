"""
Análsie léxica

Alunos: Ivair Puerari
        Jeferson Schein
"""


class Lexical:
    def __init__(self, pAutomaton, pSymbol):
        self.tableOfSymbol = []
        self.afnd = pAutomaton
        self.tape = [] #Fita
        self.terminals = pSymbol
        self.recurrentLine = None
    
    def lexicalAnalysis(self,pFile):
        log = []
        NumberOfline = 1
       
        for self.recurrentLine in open(pFile,'r'):
            self.removeAndSplitLine()
            if(self.isNotLineEmpty()):
                for symbol in self.recurrentLine:
                    state = 0
                    error = 0
                    for position in symbol:

                        newState = self.verifySymbol(position,state,symbol)
                        if(newState > max(self.afnd.keys())):
                            if(state > 0):
                                error = 1
                            break
                        else:
                            state = newState
                            
                    if(self.isStateFinal(state) and self.HaveNoErrors(error)):
                        self.setTableOfSymbol([symbol,state,NumberOfline])
                    else:
                        error = 1

                    if(not self.HaveNoErrors(error)):    
                        self.setTableOfSymbol([symbol,max(self.afnd.keys()),NumberOfline])
                        log.append("\nErro Léxico! >> Token:"+ symbol + " Linha : "+str(NumberOfline))

            NumberOfline += 1 
        
        return self.infoLog(log)                    
    
    def verifySymbol(self, pPosition, pState, pSymbol):
        for state in range(0,len(self.afnd[pState])):
            newState = self.afnd[pState][state].split(":")
            if(pPosition in newState[0]):
                newState = int(newState[1])
                return newState
        return max(self.afnd.keys())+1
    
    def removeAndSplitLine(self):
        self.recurrentLine = self.recurrentLine.strip().split()

    def infoLog(self,pLog):
        if(len(pLog) > 0):
            for line in pLog:
                print(line + '\n')
            return False
        else:
            print('\nNenhum erro léxico!\n')
            return True
            
    def setTableOfSymbol(self,pValue):
        self.tableOfSymbol.append(pValue)
    
    def isStateFinal(self, pState):
        return (pState in self.terminals.keys())  
    
    def HaveNoErrors(self,pError):
        return (pError == 0)  
    
    def isNotLineEmpty(self):
        return (self.recurrentLine != '')   

         
