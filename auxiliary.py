import pygame
from random import choices
from settings import *
from copy import deepcopy


# Predicates

def isFire(layout, i, j):
	return layout[i][j] == 'F'

def isSmoke(layout, i, j):
	return layout[i][j] == 'S'

def isWall(layout, i, j):
	return layout[i][j] == 'W'

def isExit(layout, i, j):
	return layout[i][j] == 'E'

def isAlarm(layout, i, j):
	return layout[i][j] == 'A'

def validPropagation(layout, i, j):
	return not isWall(layout,i,j) and not isFire(layout,i,j) and not isSmoke(layout,i,j) and not isExit(layout,i,j)


# Auxiliar

def getLayout(file):
    #f = open('supermarket.txt', 'r').read()
	if(file is None): f = open('supermarket.txt', 'r').read()
	else: f = open(file, 'r').read()
	p = []
	p = [item.split() for item in f.split('\n')[:-1]]
	return p

def getExitsPos(layout):
	return [ [index, row.index('E')] for index, row in enumerate(layout) if 'E' in row]