#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:55:28 2019

@author: ananthu
"""
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import pandas as pd

#Function converting pdf to string
def convert(fname):
    with open(fname, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            
            # create a file handle
            fake_file_handle = io.StringIO()
            
            # creating a text converter object
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            # process current page
            page_interpreter.process_page(page)
            
            # extract text
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()
            
import spacy

def extract_name(text):
    text = text.split("\n")
    text = [x.lstrip() for x in text]
    while('' in text) : 
        text.remove('') 
    print(text[0])
    
    
import re

def extract_mobile_number(text):
    text = text.split("\n")
    for w in text:
        w= w.replace('·','-')
        phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), w)
        if(phone):
            ph=""
            for x in phone[0]:
                ph+=str(x)
            break;
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number
        
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None


def extract_skills(resume_text):
    # load pre-trained model
    nlp = spacy.load('en_core_web_sm')
    nlp_text = nlp(resume_text)
    noun_chunks =nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("skills.csv") 
    
    # extract values
    skills = list(data.columns.values)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

files=[]
import glob, os
os.chdir("./")
for f in glob.glob("*.pdf"):
    files.append(f)

for f in files:
    text=""
    print(f)
    for page in convert(f):
            text += ' ' + page
    extract_name(text)
    text = text.replace(',',' ')
    #Converting all the charachters in lower case
    text = text.lower()
    print("Phone : " +str(extract_mobile_number(text)))
    print("email : " +str(extract_email(text)))
    print(extract_skills(text))
    print("\n")

