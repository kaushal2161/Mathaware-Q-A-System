import json
from flask import jsonify
from sympy.core.sympify import sympify
from sympy import Number, NumberSymbol, Symbol


def evalformula(formula):
    #f=process_sympy(formula)
    a=sympify(formula)    
    symbol=a.atoms(Symbol)    
    return symbol
    

def value(formula):
    #f=process_sympy(formula)
    a=sympify(formula)
    symbol=a.atoms(Symbol)
    return symbol


def equality(formula,ext):
    global lhs
    global rhs    
    lhs,rhs=formula.split(ext,1)    
    value=evalformula(rhs)
    return value   

def formuladivision(formula):    
    k = ['=', '\leq', '\req', '\\approx']         
    if '=' in formula:
        ext = '='              
        return ext
                    
    if '\leq' in formula:
        ext = '\leq' 
        return ext
                
    if '\req' in formula:
        ext = '\req'  
        return ext
                
    if '\\approx' in formula:
        ext = '\\approx'           
        return ext
                
    if not any(ext in formula for ext in k):   
        return None
    


class Getidentifiers:
    def __init__(self, request):
        self.request = request           
        
        
    def answer(self):  
        formula=self.request 
        global seprator 
        self.seprator= formuladivision(formula)
        if self.seprator is not None:
            symbol=equality(formula,self.seprator)
        else:
            symbol=value(formula)
            
        listsymbol=list(symbol)                    
        #string=''.join(str(listsymbol))
        return listsymbol
 