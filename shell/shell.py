#!/usr/bin/env python3

import os, sys, re
'''
OS gives us access to the read and write function
sys gives us the ability to exit if needed
re gives us
'''
#methods below are all to dedicated to handling instructions given in the shell
#either commands or starting a process etc

def reDir(param):
    return

def pipe(param):
    #piping means two progs share their ifnormaion while running
    leftProg = param[:param.index('|')]
    rightProg = param[param.index('|')+1:]

    pr, pw = os.pipe() #parent write and read
    for f in (pr,pw): #allow child to inheret
        os.set_inheritable(f, True)

    rc = os,fork() #child process

    #check the child | copied from exeProg 
    if rc < 0:
        os.write(2, 'fork failed, returning %d\n' %rc).encode())
        sys.exit(1)
        
    elif rc == 0:
        os.close(1) #close output file
        os.dup(pw) #use parent write

        for fd in (pr, pw): #close the file descriptors
            os.close(fd)
        exeProg(leftProg) #compute one portion of the pipe
        os.write(2, ('Could not execute %s\n' %leftProg[0]).encode()) #incase of error
        sys.exit(1)

    else:
        os.close(0) #input file
        os.dup(pr) #use parent read

        for fd in (pr, pw):
            os.close(fd)
        if '|' in rightProg: #if there is another pipe command
            pipe(rightProg) #call our pipe method

        exeProg(rightProg) #parent does right of pipe
        os.write(2, ('Could not execute %s\n' %rightProg[0]).encode())
        sys.exit(1)
            
    print(leftProg)
    print(rightProg)
    return


def exeProg(param):
    #directly for commands
    for dir in re.split(':', os.environ['PATH']):#go in all directories
        prog = '%s/%s'% (dir,param[0]) #get the first command
        try:
            os.execve(prog, param, os.environ)
        except FileNotFoundError:
            pass #fail smoothly
    os.write(2, ("Could not exec. File not Found: %s\n" % param[0]).encode())
    sys.exit(1) #terminate with error


def ident_Input(userIn):
    wait_child = True #by default we always want to wait

    if len(userIn) <= 0:
        return #empty, no point
    
    elif userIn[0].lower() == 'exit': #generic all exit input | exit always be first
        os.write(1, 'Have a good day!\n\n'.encode())
        sys.exit(1)

        #comands following
    elif userIn[0] == 'cd': #change directory is built in function
        try:
            for i in userIn[1:]:
                os.chdir(i) #change directory
        except FileNotFoundError:
            os.write(1, ('No such directory found\n').encode())

    elif '&' in userIn:
        wait_child = False #& means to run in the background

    elif '|' in userIn:
        pipe(userIn)

    elif '<' in userIn or '>' in userIn:
        print('We are redirecting')

    else: #other commmand from /usr/bin
        rc = os.fork() #child of shell prog
        if rc < 0: #taken from Dr. Freudenthal's Demo - p2-wait.py
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0: #we have the child
            exeProg(userIn) #child process will execute the command
            sys.exit(1) #terminate child
        else:
            if wait_child: #we wait for the child
                child_Proc = os.wait() #waits on the child
            #if ampersand we do not wait for the child 

while True: #this allows shell to always be ready for input
    if 'PS1' in os.environ: #if there is custom prompt 1 then it re prints it out
        os.write(1, os.environ['PS1'].encode())
    else: # we set our own prompt
        os.write(1, ('@> ').encode())

    #account for user input
    #accept user commands
    try: #error handling with os.read
        userIn = os.read(0,1024) #acts like myreadline and passes entirity of what is read
        if (len(userIn)>1):#input detected
            userIn = userIn.decode().split('\n') #remove end of line
            for i in userIn:
                ident_Input(i.split()) #tokenize input
        #if empty it will still keep running

    except EOFError:
        os.write(1, ('There has been an error').encode())
