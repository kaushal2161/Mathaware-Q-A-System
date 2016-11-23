from flask import Flask
from flask import request
from flask import render_template
import json
from process_latex import process_sympy
from flask.json import jsonify
from sympy.core.sympify import sympify
from sympy import Number, NumberSymbol, Symbol
from getidentifiers import Getidentifiers
import getidentifiers
import os
import re
import requests
from ppp_datamodel import Sentence, Request, Response
import latexformlaidentifiers
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
os.environ['PPP_QUESTIONPARSING_GRAMMATICAL_CONFIG'] = 'ppp_questionparsing_grammatical/nlp_classical_config.json'
from ppp_datamodel.communication import Request
from ppp_questionparsing_grammatical import RequestHandler
from getformula import FormulaRequestHandler
from getformula import HindiRequestHandler 
from latexformlaidentifiers import Formulacalculation, prepformula


def getlhsrhs(formula,ext):
    global lhs
    global rhs    
    lhs,rhs=formula.split(ext,1)  
    
def makeidentifier(symbol,values):    
    symvalue={}
    for i in symbol:              
        for j in values:           
            if i==Symbol(j):                
                value=values[j]                
                symvalue[i]=value 
                  
    return symvalue

def makerespose(formul):
    try:
        reques=Formulacalculation(formul)                         
        global identifiers
        identifiers=reques.answer()
        if identifiers:
            listidentifiers=list(identifiers)
            
            newlist= []
            for item in listidentifiers:
                newlist.append(str(item))            
                
            newlist.append(dict(formula=formul))               
            
            resp=json.dumps(newlist) 
            #print(resp) 
            return resp   
        else:
            resp=json.dumps(formul)          
            return resp  
    except Exception as e : return ("System is not able to understand the formula")
    

app = Flask(__name__)    
@app.route('/')
def my_form():
    return render_template("index.html")

@app.route('/getresponse', methods=['POST'])
def my_form_post():
    try:
        if request.form['formula']:            
            global formula                
            formula= request.form['formula']                                 
            #req=Formulacalculation(formula)                         
            #listofsybol=req.answer()  
            #print(formula.replace('/\\\\/g',''))
            global processedformula
            processedformula=latexformlaidentifiers.prepformula(formula)  
            #print(processedformula)        
            if formula is not None: 
                return makerespose(processedformula)   
            
            else:
                return ("System is not able to find the result.")      
                
                
    except Exception as e : return ("System is not able to understand the formula")
            

    
@app.route('/getengformula', methods=['POST'])
def get_formula(): 
       
    try:
        question=request.form['formula']        
        meas = {'accuracy': 0.5, 'relevance': 0.5}
        q = RequestHandler(Request(language="en",id=1,tree=Sentence(question),measures=meas))
        query = q.answer()           
        reques= FormulaRequestHandler(query) 
        global formula        
        formula=reques.answer() 
        #print(formula)
        global processedformula
        processedformula=latexformlaidentifiers.prepformula(formula)  
        #print(processedformula)     
        if formula is not None: 
            return makerespose(processedformula)       
            
        else:
            return ("System is not able to find the result.")
    except Exception : return ("System is not able to find the result.") 
    
@app.route('/gethindiformula', methods=['POST'])
def get_hindiformula():    
    
    try: 
        question=request.form['formula']        
        matchObj = re.match( r'(.*)की (.*?) .*', question, re.M|re.I)
        matchObj1 = re.match( r'(.*)के लिए (.*?) क्या है *', question, re.M|re.I) 
        matchObj2 = re.match( r'(.*)और (.*?) के बीच *', question, re.M|re.I)
        if matchObj:
            subject=matchObj.group(1)
            predicate=matchObj.group(2)  
            
        if matchObj1:
            subject=matchObj1.group(1)
            predicate=matchObj1.group(2)  

        if matchObj2:
            subject=matchObj2.group(1)
            predicate=matchObj2.group(2)          
         
        reques = HindiRequestHandler("hi",subject,predicate)
        global formula
        formula=reques.answer()
        global processedformula
        processedformula=latexformlaidentifiers.prepformula(formula)            
        if formula is not None:            
            return makerespose(processedformula)
        else:
            return ("System is not able to find the result.")             
        
    except Exception : return ("System is not able to find the result.") 
        

@app.route('/getfinalresult', methods=['POST'])
def my_form_json():  
       
       
        identifiers1 = request.data.decode('utf-8')    
        json1=json.loads(identifiers1)                      
        seprator= getidentifiers.formuladivision(formula)
        if seprator is not None:               
            lhsrhs= getlhsrhs(processedformula,seprator)            
            f=process_sympy(rhs)
            f1=process_sympy(lhs)
            latexlhs=sympify(f1)    
            l=sympify(f) 
            #print(l)
            symbolvalue=makeidentifier(identifiers,json1)           
            value=l.evalf(subs=symbolvalue)  
               
            return ("%s %s %.2e" % (latexlhs,seprator,value))
        else:
            l=sympify(formula)             
            value=l.evalf(subs=json1)
                
            return ("%.2e" % value)
            
    #except Exception : return ("System is not able to calculate the result.")   
  
if __name__ == '__main__':
    app.run(debug=True)
    #get_formula()