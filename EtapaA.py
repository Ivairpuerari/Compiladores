from LexicaA import *

compilador = Lexical("tokens.txt")
compilador.lexicalAnalysis("test.txt")

if compilador.done:
    print("Fita> ",compilador.tape)
    print('\nTabela de simbolos> ',compilador.tableOfSymbol)