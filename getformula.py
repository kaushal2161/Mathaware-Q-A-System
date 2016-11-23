# -*- coding: utf-8 -*-
"""Request handler of the module."""

import pywikibot
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, JSON
import xmltodict

formula=defaultdict(list)

def get_formula(sub,lang="en"):
    """
        Get subject number and language 
        Return value of defining formula property:P2534
    """
    try:
        subject= str(sub)        
        site = pywikibot.Site(lang, "wikipedia")
        page = pywikibot.Page(site,subject)
        item = pywikibot.ItemPage.fromPage(page)
        
        # Get the claim dictionary
        item_dict = item.get()
        clm_dict = item_dict["claims"]
        
        # Get the defining formula property:P2534
        for clm in clm_dict["P2534"]:
            key=clm.getTarget()
            return key
        
        
    except:
        #error=("Formula for item " + sub + " could not be found.")
        return []
    ''' 
    try:   
        for clm in clm_dict["P527"]:
            #c=clm.getTarget()
            json=clm.toJSON()
            #print(json)
            #print(json['qualifiers']['P2534'][0]['datavalue']['value'])
            formula[key].append(json['qualifiers']['P2534'][0]['datavalue']['value'])
            return formula
        
    except:
        return key    
    '''
 
def get_formula_geometry(sub,pred): 
    """
        Get subject and predicate number
        Return value of has quality property : P1552
    """
    
    item_dict = sub.get()
    clm_dict = item_dict["claims"] 
    try:
        #get the has quality property:P1552
        for clm in clm_dict["P1552"]:
            c=clm.getTarget()      
            if c == pred:
                c=clm.toJSON()
                
                return (c['qualifiers']['P2534'][0]['datavalue']['value'])
                
            else:
                pass
    except:
        #error= ("Formula for item " + sub + " could not be found.")
        return []
        
def get_formula_sparql(sub,pred):
    """
        Get subject and predicate number 
        return formula
    """
    subn=str(sub).replace("[[wikidata:",'').replace("]]",'')
    predn=str(pred).replace("[[wikidata:",'').replace("]]",'')
    
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    try:
        q="""
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        
        SELECT ?qid ?qformula WHERE {
            ?qid wdt:P527 wd:%s.
              ?qid wdt:P527 wd:%s.
              ?qid wdt:P2534 ?qformula.
              
          
          }"""%(subn,predn)
        sparql.setQuery(q)
        
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            #print(result["p"]["value"]) + " " + result["w"]["value"]
            a=result["qformula"]["value"]
            
        result = xmltodict.parse(a)
        return (result['math']['semantics']['annotation']['#text'])
        
    except:
        #error=("Formula for item " + sub + " could not be found.")
        return []

Hindigeolist=['क्षेत्रफल', 'आयतन' ,'समुद्र तट से ऊंचाई', 'लम्बाई','विकर्ण','सतह क्षेत्र','लंबाई']
def get_item_number(subject,predicate,lang="en"):
    """
        Get subject, predicate and language
        Return formula
    """
    
    try:    
        usub=str(subject)
        upred=str(predicate)         
        site = pywikibot.Site(lang, "wikipedia")
        subjecti= pywikibot.Page(site,usub)           
        sitem = pywikibot.ItemPage.fromPage(subjecti)        
        predicatei= pywikibot.Page(site, upred)  
        pitem = pywikibot.ItemPage.fromPage(predicatei)        
        if(lang=="en"):                       
            return get_formula_geometry(sitem,pitem)        
        if upred in Hindigeolist:           
            return get_formula_geometry(sitem, pitem)        
        else:
            return get_formula_sparql(sitem,pitem)
    except:
        #error= ("item " + upred + " could not be found in Wikidata.")
        return []   
    
 

 
geometry=['surface area','volume','area','radius of circle','altitude','diagonal','medians','inradius','circumradius','length']
formulalist=['formula','equation','mathematical formula']
def predicate(predicate,subject):    
    
    if predicate in geometry:        
        return get_item_number(subject,predicate)
    elif predicate in formulalist:              
        return get_formula(subject)
        
class FormulaRequestHandler:
    
    def __init__(self, request):
        self.request = request        
        
        
    def answer(self):
        request=self.request
        formula=predicate(request.predicate.value,request.subject.value)
        return formula
        
      
class HindiRequestHandler:
    
    def __init__(self, language,subject,predicate):
        self.language = language
        self.subject=subject
        self.predicate=predicate       
            
    
    def answer(self):
        
        Hindiformulalist=['गणितीय सूत्र','सूत्र','फार्मूला']
        if self.predicate in Hindiformulalist:
            return get_formula(self.subject,self.language)
        else:
            return get_item_number(self.subject,self.predicate,self.language)
        
            
        