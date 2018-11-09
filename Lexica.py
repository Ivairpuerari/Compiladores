"""
Análsie léxica

Alunos: Ivair Puerari
        Jeferson Schein
"""
from Afnd import determinizeAFND

class Lexical:
    def __init__(self, ptokens):
        self.tableOfSymbol = []
        self.afnd = determinizeAFND(ptokens)
        self.tape = [] #Fita
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
                        if self.afnd.HaveNoSymbolYet(position):
                            if(state > 0):
                                error = 1
                            break
                        else:
                            state = self.getState(position,state)
                            
                    if(self.isStateFinal(state) and self.HaveNoErrors(error)):
                        self.setTableOfSymbol([symbol,state,NumberOfline])
                        self.setTape([symbol,state])
                    else:
                        self.setTableOfSymbol([symbol,max(self.afnd.automaton.keys()),NumberOfline])
                        self.setTape([symbol,max(self.afnd.automaton.keys())])
                        log.append("Erro Lexico! Token:"+ symbol + " Linha : "+str(NumberOfline))

            NumberOfline += 1 
        
        self.infoLog(log)                    

    def removeAndSplitLine(self):
        self.recurrentLine = self.recurrentLine.strip().split()
    def setTape(self,pValue):
        self.tape.append(pValue)


    def infoLog(self,pLog):
        self.Show(pLog) if len(pLog) > 0 else print("Nenhum erro lexico!")
    def Show(self,pLog):
        for line in pLog:
            print(line + '\n')
            
    def setTableOfSymbol(self,pValue):
        self.tableOfSymbol.append(pValue)
    
    def isStateFinal(self, pState):
        return (pState in self.afnd.FinalStates)  
    
    def HaveNoErrors(self,pError):
        return (pError == 0)  
    
    def getState(self,pPosition,pState):
        index = self.afnd.symbols.index(ord(pPosition))
        return self.afnd.automaton[pState][index]
    
    def isNotLineEmpty(self):
        return (self.recurrentLine != '')             

if __name__ == '__main__':	
	lex = Lexical("tokens.txt")
	lex.lexicalAnalysis("test.txt")
	print(lex.tape)
	print('\n',lex.tableOfSymbol)