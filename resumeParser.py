#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 12:55:28 2019

@author: ananthu
"""
import io,os,subprocess
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import pandas as pd

from docx import Document
#docx to text
def convertDocxToText(path):
    document = Document(path)
    return "\n".join([para.text for para in document.paragraphs])
#doc to text
def getDocText(fileName):
    extension="doc"
    doc =subprocess.Popen(['antiword', fileName], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0], extension
    return str(doc[0].decode('ascii', 'ignore'))
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
import nltk
def extract_name(Otext):
    temp=0
    text = Otext.split("\n")
    text = [x.lstrip() for x in text]
    while('' in text) : 
        text.remove('') 
    
    for sent in nltk.sent_tokenize(Otext):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label'):
                    l =(' '.join(c[0] for c in chunk))
                    if(chunk.label()=='PERSON' and not temp):
                        name=l
                        temp=1
                    if(l in text[0] or text[0] in l):
                        return text[0]
    return name
        
    #print("Name :"+str(temp))

import re

def extract_mobile_number(text):
    text = text.split("\n")
    for w in text:
        w= w.replace('·','-')
        w= w.replace('-','')
        phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4}|[0-9]{3})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), w)
        if(phone):
            ph=""
            for x in phone[0]:
                ph+=str(x)
            if(len(ph)>=10):
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

# load pre-trained model

def extract_skills(nlp_text):
    
    noun_chunks =nlp_text.noun_chunks
    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    #print(tokens)
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



from nltk.corpus import stopwords

def extract_education(nlp_text):
    # Grad all general stop words
    STOPWORDS = set(stopwords.words('english'))

    # Education Degrees
    EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH','M.TECH', 'MTECH','TECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','ISC'
            ]
    st_words=['Be','be','me','Me']
    # Sentence Tokenizer
    nlp_text = [sent.string.strip() for sent in nlp_text.sents]
    edu = set()
    # Extract education degree
    for index, text in enumerate(nlp_text):
        
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex.upper() not in STOPWORDS and tex not in st_words:
                edu.add(tex.upper())
    return list(edu)

def resumeParse(filename,location):
    files=[]
    import glob
    os.chdir(location)
    text=""
    extension=filename.split(".")[1]
    if(extension=="pdf"):
        for page in convert(filename):
            text += ' ' + page
    elif(extension=="doc"):
        text=getDocText(filename)
    elif(extension=="docx"):
        text=convertDocxToText(filename)
    resume_data={}
    resume_data["Name"]=extract_name(text)
    resume_data["Phone"]=str(extract_mobile_number(text))
    resume_data["Email"]=str(extract_email(text))
    nlp = spacy.load('en_core_web_sm')
    nlp_text = nlp(text)
    resume_data["Skills"]=str(extract_skills(nlp_text))
    resume_data["Education"]=str(extract_education(nlp_text))
    print(resume_data["Name"]+"\n")
    return resume_data

