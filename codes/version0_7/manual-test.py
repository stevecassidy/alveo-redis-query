'''
Created on 24 Jul 2014

@author: ehsan
'''
import os
import string


if __name__=='__main__':
    filename = './samples/test/sample12.txt'
    text = ""
    with open(filename, 'r') as f:
        text = f.read().lower()
    indices = []
    index = text.find('10.30am')
    print index
    