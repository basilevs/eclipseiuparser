#!/bin/python3
from feature import get_feature
from sys import argv
from pprint import pprint

if __name__ == '__main__':
	pprint(get_feature('.', argv[1]))