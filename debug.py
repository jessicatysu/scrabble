#!/usr/bin/python

def log(msg):
    log = open("log.txt", "a")
    log.write(msg + "\n")
    log.close()
