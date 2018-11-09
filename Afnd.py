from collections import defaultdict
import itertools

class determinizeAFND:
    def __init__(self, pTokens):
        self.NameFile = 'tokens.txt' #ptokens
        self.states = 0
        self.done = False
        self.automaton = defaultdict(list)
        self.mapGramatic = {}
        self.symbols =  list()
        self.StatesRemoved = {}
        self.RecurrentLine = None
        self.FinalStates = list()
        self.BuildingAFND()
        self.determinize()

    def determinize(self):
        keys = self.getListOfKeysAutomoton()
        for indexKey in keys:
            state = self.GetValueKey(indexKey)
            initState = state

            if self.IsNotStateRule(state):
                state = state.split(",")
                state = [(position.strip()) for position in state]
                data= []

                for indexSymbol in range(len(self.symbols)):
                    newValue = list()
                    for value in state:
                        firstTest = self.GetValueKey(int(value))
                        secondTest = self.GetValueKey(indexKey) 

                        if self.TestTypeState(firstTest,secondTest):
                            copyValue = self.mapGramatic[initState]
                            self.mapGramatic[initState+"f"] = copyValue 
                            self.mapGramatic.pop(initState)
                        
                        if (self.IsNotAutomatonEmpty(int(value),indexSymbol)):
                            if(self.automaton[int(value)][indexSymbol] not in newValue):
                                newValue.append(self.automaton[int(value)][indexSymbol])
                
                    if (len(newValue) == 1):
                        self.automaton[indexKey][indexSymbol] = newValue[0]
                        data.append((str(chr(self.symbols[indexSymbol]))+":"+str(newValue[0])))
                
                    if (len(newValue) >= 2 ) :
                        self.SearchStatesEqualsAndAddState(indexKey,indexSymbol,newValue)
                        newState = [str(position) for position in newValue] 
                        newState = ','.join(newState)   
            else:
                for(index,value) in enumerate(self.automaton[indexKey]):
                    if self.IsHaveInderminism(value):
                        self.SearchStatesEqualsAndAddState(indexKey,index,value)
                        newState = [str(position) for position in value]
                        newState = ','.join(newState)
            if self.IsKeysInc(keys):
                copyValue = set(self.automaton.keys()) - set(keys)
                [keys.append(newKey) for newKey in copyValue]
        
        
        self.Minimize()
        self.FillAllTable()
        self.done = True

    def FillAllTable(self):
        self.mapGramatic["Xf"] = self.states

        for key in self.automaton.keys():
            for index in range(len(self.automaton[key])):
                if self.IsNotAutomatonEmpty(key,index) == False:
                    self.automaton[key][index] = self.states
        
        self.automaton[self.states] = [self.states] * len(self.symbols)
        self.IncNumberOfStates()

    def Minimize(self):
        copyAutomaton = self.automaton.copy()
        visited = self.DFS(0,copyAutomaton)
        diff = list (set(copyAutomaton.keys()) - visited )
        if len(diff) > 0:
            self.RemoveStates(diff)
        
        states = []
        for value in self.mapGramatic.values():
            test = self.GetValueKey(value)
            if self.isStateFinal(test):
                states.append(self.mapGramatic[test])
        self.FinalStates[:] = states

        for key in list(self.automaton):
            if('TEf' in self.mapGramatic):
                if(self.mapGramatic['TEf'] == key) :
                    continue
            visited = self.DFS(key,copyAutomaton)
            visitedYet = True
            for state in states:
                if( state in list(visited)):
                    visitedYet = False
            if visitedYet:
                self.RemoveStates([key])

    def StateVisited(self, pStates,pNodes):
        for state in pStates:
            if( state in list(pNodes)):
                return False
        return True

    def RemoveStates(self,pStates):
        for index in pStates:
            removed = self.GetValueKey(int(index))
            self.StatesRemoved[removed] = self.mapGramatic[removed]
            self.mapGramatic.pop(removed)
            self.automaton.pop(index)


    def DFS(self, init, pAutomaton ):
        visited = set()
        stack = [init]
        
        while stack:
            state = stack.pop()
            if(state not in visited):
                visited.add(state)
                stack.extend(set(pAutomaton[state]) - visited)

                if('' in stack):
                    count = stack.count('')
                    for i in range(int(count)):
                        stack.pop(stack.index(''))
        return visited

    def UpdateKeys(self, pkeys,pcopyValue):
        return [pkeys.append(newKey) for newKey in pcopyValue]

    def IsKeysInc(self, pkeys):
        return (len(self.automaton.keys()) > len(pkeys))
    
    def TestTypeState(self, pFirstTest,pSecondTest):
        return ( self.isStateFinal(pFirstTest) and ( "f" not in pSecondTest ))
    
    def SearchStatesEqualsAndAddState(self, pIndexKey, pIndex, pvalue):
         
        permutatioValues = self.getListOfCombinations(pvalue)
        addState = True
        for value in permutatioValues:
            state = str(value)
            state = state[1:-1]  ##remove '()'
            if (state in self.mapGramatic) or (state+"f" in self.mapGramatic):
                addState = False
        pvalue = str(pvalue)
        pvalue = pvalue[1:-1]

        if(pvalue+"f" in self.mapGramatic):
            pvalue = pvalue + "f"

        if addState:
            self.mapGramatic[pvalue] = self.states
            self.automaton[self.states] = ['']*len(self.symbols)
            self.IncNumberOfStates()
            ##self.setState(pvalue)  
        self.automaton[pIndexKey][pIndex] = self.mapGramatic[pvalue]

    def getListOfCombinations(self, pvalue):
        return list(itertools.permutations(pvalue))

    def IsHaveInderminism(self,pvalue):
        return (type(pvalue) is list) 
    
    def IsNotStateRule(self,pState):
        return (pState[0].isalpha() is not True)

    
    def GetValueKey(self,pindex):
        for key, value in self.mapGramatic.items():
            if value == pindex:
                return key
    
    def getListOfKeysAutomoton(self):
        return list(self.automaton.keys())
    
    def BuildingAFND(self):
        self.FillTableOfSymbol()  
        self.HandlingTypesInInput()

    
    def HandlingTypesInInput(self):
        for self.RecurrentLine in open(self.NameFile,'r'):
            self.ReadGrammar() if self.isGrammar() else self.ReadToken()

    
    def ReadToken(self):
        self.RemoveAndSplitToken()

        if self.HaveStateYet('Sf'):
            SymbolThatGetNameOfRule = 'Sf'  
        else:
            SymbolThatGetNameOfRule = 'S'

        for i in range(0,len(self.RecurrentLine)):
            if self.isEmptyStates():
                self.setState(SymbolThatGetNameOfRule)
            if self.isOneSizeToken(i):
                state = 'T' + str(self.states) + 'f'
            else:
                state = 'T' + str(self.states)

            if self.HaveNoStateYet(state):
                self.setState(state)
            self.isSymbolDeterministic(self.RecurrentLine[i],state,SymbolThatGetNameOfRule)
            SymbolThatGetNameOfRule = state
            
    def isOneSizeToken(self,pI):
        return (pI == (len(self.RecurrentLine) - 1))
    
    def isEmptyStates(self):
        return (self.states == 0)


    def ReadGrammar(self):
        self.RemoveAndSplitGrammar()
        position = self.findPosition(0)

        if position.get('x_one') < 0 or position.get('x_two') < 0:
            return None
        
        state = self.getState(0,position)
        if self.HaveNoStateYet(state):
            self.setState(state)
        

        SymbolThatGetNameOfRule = state
        for i in range(1,len(self.RecurrentLine)):
            if self.isNotRuleEmpty(i):
                position = self.findPosition(i)
                state = self.getState(i,position)
                
                if position.get('x_one') < 0 or position.get('x_two') < 0: # |a| É TERMINAL
                    state = 'TEf'
                    if self.HaveNoStateYet(state):
                        self.setState(state)
                    self.isSymbolDeterministic(self.RecurrentLine[i],state,SymbolThatGetNameOfRule)
                else:
                    if self.HaveStateYet(state + "f"):
                        state = state + "f"
                    if self.HaveNoStateYet(state):
                        self.setState(state)
                    self.isSymbolDeterministic(self.getProduction(self.RecurrentLine[i],position),state,SymbolThatGetNameOfRule)
                    
    def isSymbolDeterministic(self,pSymbol,pState,pSymbolThatGetNameOfRule):
        idxState = self.mapGramatic[pState]
        idxSymbolThatGetNameOfRule = self.mapGramatic[pSymbolThatGetNameOfRule]
        idxSymbol = self.symbols.index(ord(pSymbol))
        
        if(self.IsNotAutomatonEmpty(idxSymbolThatGetNameOfRule,idxSymbol)):
            value = self.getValueAutomaton(idxSymbolThatGetNameOfRule,idxSymbol)
            if idxState not in value:
                value.append(self.mapGramatic[pState])
                if len(value) > len([self.automaton[idxSymbolThatGetNameOfRule][idxSymbol]]):
                     self.automaton[idxSymbolThatGetNameOfRule][idxSymbol] = value
        else: 
            self.automaton[idxSymbolThatGetNameOfRule][idxSymbol] = self.mapGramatic[pState] 
    
    def IsNotAutomatonEmpty(self,pIdxSymbolThatGetNameOfRule,pIdxSymbol):
        return (self.automaton[pIdxSymbolThatGetNameOfRule][pIdxSymbol] != '')

    def getValueAutomaton(self,pIdxSymbolThatGetNameOfRule,pIdxSymbol):
        if(type(self.automaton[pIdxSymbolThatGetNameOfRule][pIdxSymbol]) is list):
            return self.automaton[pIdxSymbolThatGetNameOfRule][pIdxSymbol]
        else:
            return [self.automaton[pIdxSymbolThatGetNameOfRule][pIdxSymbol]]

    def getState(self,pI,pPosition):
        return self.RecurrentLine[pI][pPosition.get('x_one')+1:pPosition.get('x_two')] + self.getTypeGrammar()
    
    def isNotRuleEmpty(self,pI):
        return (self.RecurrentLine[pI] != ' ' and self.RecurrentLine[pI] != '')
    
    def setState(self,pState):
        if 'S' == pState:
            self.mapGramatic[pState] = 0
            self.automaton[0] = ['']*len(self.symbols)
            self.IncNumberOfStates()
        elif self.isStateFinal(pState) and self.HaveStateYet(pState[0:-1]):
            self.mapGramatic[pState] = self.mapGramatic[pState[0:-1]]  ##SERA?
            self.mapGramatic.pop(pState[0:-1])
        else:
            self.mapGramatic[pState] = self.states
            self.automaton[self.states] = ['']*len(self.symbols)
            self.IncNumberOfStates()
    
    def isStateFinal(self,pState):
        return ('f' in pState)
    
    def HaveStateYet(self,pState):
        return (pState in self.mapGramatic.keys())
    
    def HaveNoStateYet(self,pState):
        return (pState not in self.mapGramatic.keys())
   
    def IncNumberOfStates(self):
        self.states += 1
   
    def getTypeGrammar(self):
        if self.IsGrammarFinal():
            return "f"
        else:
            return ""
    
    def IsGrammarFinal(self):
        return ('' in self.RecurrentLine or ' ' in self.RecurrentLine)
    
    def FillTableOfSymbol(self):
        ##fileReader = open(self.NameFile,'r')
        for self.RecurrentLine in open(self.NameFile,'r'):    
                self.SetAlphabetSymbols()
 
    def HandlingLines(self):
        self.RemoveAndSplitGrammar() if self.isGrammar() else self.RemoveAndSplitToken
        

    def isGrammar(self):
        return "::=" in self.RecurrentLine

    def RemoveAndSplitGrammar(self):
        self.RecurrentLine = self.RecurrentLine.replace(':=', '|')
        self.RecurrentLine = self.RecurrentLine.split('|')
        self.RecurrentLine = [(rule.strip()) for rule in self.RecurrentLine]


    def RemoveAndSplitToken(self):
        self.RecurrentLine = self.RecurrentLine.strip()

    def findPosition(self,pCaracter):
        return {'x_one': self.RecurrentLine[pCaracter].find("<"), 'x_two': self.RecurrentLine[pCaracter].find('>') }
    
    def SetAlphabetSymbols(self):
        if self.isGrammar():
            self.RemoveAndSplitGrammar()
            
            for Icaracter in range(1,len(self.RecurrentLine)):
                position = self.findPosition(Icaracter)
            
                if position.get('x_one')>= 0 and position.get('x_two') >= 0:
                    symbol = self.getProduction(self.RecurrentLine[Icaracter],position)
                    if self.HaveNoSymbolYet(symbol):
                        self.symbols.append(ord(symbol))   
                
                elif(len(self.RecurrentLine[Icaracter])==1):
                    if self.HaveNoSymbolYet(self.RecurrentLine[Icaracter]):
                        self.symbols.append(ord(self.RecurrentLine))
        else:
            self.RemoveAndSplitToken()
            for Icaracter in range(0,len(self.RecurrentLine)):
                if self.HaveNoSymbolYet(self.RecurrentLine[Icaracter]) and self.RecurrentLine[Icaracter] != " " :
                    self.symbols.append(ord(self.RecurrentLine[Icaracter]))
          
    def HaveNoSymbolYet(self,pSymbol):
        return ord(pSymbol) not in self.symbols

    def getProduction(self, Pprod,Pposition):
        if Pposition.get('x_one') > 0:
            return Pprod[0:Pposition.get('x_one')]
        else:
            return Pprod[Pposition.get('x_two') + 1: -1]



def main():
    afnd = determinizeAFND('tokens.txt')


if __name__ == '__main__':
    main()
