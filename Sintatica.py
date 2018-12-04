import sys
from collections import defaultdict
from Lexica import *
from Stack import *

'''
Analise Sintatica
    Ivair puerari,
    Jeferson schein
'''

class Syntax:
    def __init__(self, pGrammar,pInput):
        self.DFA_Final = {}  #automato
        self.LALR = {}  #produções da gramatica
        self.terminals = {}
        self.nonTerminals = {}
        self.SLR = defaultdict(list) #simbolos do alfabeto da linguagem
        self.DFA_States = defaultdict(list) #simbolos da pilha
        self.rules = []
        self.recurrentLine = None
        self.controlSteps = None
        self.state = ''
        self.flagLA = False
        self.flagTB = False
        self.readGoldParserFile(pGrammar)
        self.lex = Lexical(self.DFA_States,self.DFA_Final)
        self.lexFlag = False
        self.stack = None
        if(self.lex.lexicalAnalysis(pInput)==True):
            self.lexFlag = True      

    #Leitura da tabela de parse gerado pela ferramenta.
    def readGoldParserFile(self, pGrammar):
        for self.recurrentLine in open(pGrammar,'r'):
            if(self.isNotLineEmpty()): break
           
            if(self.isLALR()):
                self.setLALR()
            elif(self.isDFA()):
                self.setDFA()
            elif(self.isRule()):
                self.setRule()
            elif(self.isNonTerminals()):
                self.setNonTerminals()
            elif(self.isTerminal()):
                self.setTerminals()
           
    def isLALR(self):
        return (('LALR States' in self.recurrentLine) or (self.controlSteps == 'ReadLALR'))
    
    def setLALR(self):
        if(self.controlSteps != 'ReadLALR'):
            self.controlSteps = 'ReadLALR' 
        else:
            self.recurrentLine = self.removeAndSplit()
            self.fillLALR()
    
    def fillLALR(self):
        if(self.verifyState("State")):
            self.state = int(self.recurrentLine[1])
            self.flagLA = False
            self.flagTB = False
                    
        if(self.verifyState("tb")):
            self.flagLA = False
            self.flagTB = True
            return  
        
        if(self.verifyState("la")):
            self.flagLA = True
            self.flagTB = False
            return   
        
        if(self.flagLA):
            if(self.haveNoStateYetLALR()):
                self.LALR[self.state] = []
            self.LALR[self.state].append([' '.join(self.recurrentLine)])

        if(self.flagTB):
            #letin = 0
            if(self.haveNoStateYetSLR()):
                self.SLR[self.state] = [[''] * len(self.SLR[-1][0]), ['']*len(self.SLR[-1][1])]
           
            if(self.isProduct()):
                index = self.SLR[-1][0].index(self.recurrentLine[0])
                if(len(self.recurrentLine) == 2):
                    self.SLR[self.state][0][index] = str(self.recurrentLine[1])
                else:
                    self.SLR[self.state][0][index] = str(self.recurrentLine[1]+self.recurrentLine[2])
            else:
                index = self.SLR[-1][1].index(self.recurrentLine[0])
                self.SLR[self.state][1][index] = str(self.recurrentLine[2])


    def isProduct(self):
        return (("<" == self.recurrentLine[0][1] and len(self.recurrentLine[0])==3) or ( "<" not in self.recurrentLine[0]))
    
    def haveNoStateYetLALR(self):
        return (self.state not in self.LALR.keys())
   
    def haveNoStateYetSLR(self):
        return (self.state not in self.SLR.keys())

    def isDFA(self):
        return (('DFA' in self.recurrentLine) or (self.controlSteps == 'ReadDFA'))
    
    def setDFA(self):
        if(self.controlSteps != 'ReadDFA'):
            self.controlSteps = 'ReadDFA'
        else:
            self.recurrentLine = self.removeAndSplit()
            self.fillDFA()
    
    def fillDFA(self):
        
        if(self.verifyState("State")):
            self.state = int(self.recurrentLine[1])
            
            self.DFA_States[self.state] = []
        
        if(self.verifyState("Accept")):
            self.DFA_Final[self.state] = self.recurrentLine[1]
            
        elif(self.verifyState("Goto")):
            temp = self.recurrentLine[2] + ":" + self.recurrentLine[1]
            self.DFA_States[self.state].append(str(temp))
    
    def verifyState(self,pValue):
        return (pValue in self.recurrentLine)
   
    def isRule(self):
        return (('Rules' in self.recurrentLine) or (self.controlSteps == 'ReadRules'))

    def setRule(self):   
        if(self.controlSteps != 'ReadRules' ):
            self.controlSteps = 'ReadRules'
        else:   
            self.recurrentLine  = self.removeAndSplit()
            temp = self.recurrentLine[1]
            self.rules.append([self.recurrentLine[0],temp,' '.join(self.recurrentLine[3:])])
   
    def setNonTerminals(self):
        if(self.controlSteps != 'ReadNonterminals' ):
           self.controlSteps = 'ReadNonterminals'
        else:
            self.recurrentLine = self.removeAndSplit()
            self.SLR[-1][1].append(self.recurrentLine[1])
            self.nonTerminals[int(self.recurrentLine[0])] = self.recurrentLine[1]
    
    def isNonTerminals(self):
        return (('Nonterminals' in self.recurrentLine) or (self.controlSteps == 'ReadNonterminals'))
        
    def setTerminals(self):
        if(self.controlSteps == None):
            self.SLR[-1] = [[],[]]
        else:
            self.recurrentLine = self.removeAndSplit()
            self.SLR[-1][0].append(self.recurrentLine[1])
            self.terminals[int(self .recurrentLine[0])] = self.recurrentLine[1]
        
        self.controlSteps = 'ReadTerminals'

    def removeAndSplit(self):
        value = self.recurrentLine.strip()
        value = value.split()

        return value

    def testType(self,pType,pcontrolSteps,pStep):
        return ((pType in self.recurrentLine) or (pcontrolSteps == pStep))
    
    
    def isTerminal(self):
        return (('Terminals' in self.recurrentLine) or (self.controlSteps == 'ReadTerminals'))
    
    def isNotLineEmpty(self):
        return (self.recurrentLine == '')

    def syntaxAnalysis(self, debug = False):
        if(self.lexFlag):
            self.stack = Stack()
            self.stack.push(["",0])

            
            iTape = 0
            #
            while(1):

                if(self.finishedReadTableYet(iTape)):
                    index = 0
                else:
                    next = self.lex.tableOfSymbol[iTape]
                    state = self.DFA_Final[next[1]]
                    index = self.SLR[-1][0].index(state)

                vElement = self.SLR[self.stack.top()[1]][0][index]
                
               
                if(debug):
                    self.info()

                if(self.isReduce(vElement)):
                    self.reduce(vElement)
               
                elif(self.isShift(vElement)):
                    iTape = iTape + 1
                    self.shift(vElement,next[0])
                
                elif(self.isAccept(vElement)):
                    print("\nAnálise Sintática finalizada corretamente!\n")
                    break
                else:
                    error = self.getError(self.stack.top()[1],iTape)
                    print("\nErro sintático! >> Esperado Token " + str(error[0])+" na linha "+str(self.lex.tableOfSymbol[iTape][2])+"\n")
                    break
    def finishedReadTableYet(self,pIndex):
        return (pIndex >= len(self.lex.tableOfSymbol))

    def getError(self,pValue,pItape):
        index = [ i[0] for i in enumerate(self.SLR[pValue][0]) if i[1] != '']
        error = [self.SLR[-1][0][i] for i in index]
        error = " , ".join(error)
        desc = [i[1][0] for i in enumerate(self.lex.tableOfSymbol) if i[0] < pItape]
        desc = ' '.join(desc)
        #desc = desc + ' >#<'
        return error,desc
    
    def isAccept(self,pValue):
        return("a" in pValue)       
    
    def isShift(self,pValue):
        return ("s" in pValue)
    
    def shift(self,pValue,pState):
        self.stack.push([pState,int(pValue[1:])])
        
    
    def reduce(self,pValue):
        vReduce = int(pValue[1:])
        size = len(self.rules[vReduce][2].split())
                    
        self.stack.pop(size)
                    
        iNonterminals = self.SLR[-1][1].index(self.rules[vReduce][1])
        newValeu = self.SLR[self.stack.top()[1]][1][iNonterminals]  

        self.stack.push([self.rules[vReduce][1],int(newValeu)])

    def isReduce(self,pValue):
        return ("r" in pValue)

    def info(self):
        print("Stack: "+ str(self.stack.data))

if __name__ == "__main__":
    test = Syntax('inputGrammar.txt','test.txt')
    test.syntaxAnalysis(True)
