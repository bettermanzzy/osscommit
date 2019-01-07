# coding: utf-8
# Get tag messages from git depository.
# How to use ?  Command :python git_tag_msg.py <parameter>.
# Parameter is the name of git depository folder. for example: lz4,log4j,etc. [ note : Do not + '/ '].
from __future__ import print_function
import subprocess
import os
import sys
import re
import pandas as pd
import time
from tqdm import tqdm

git_cmd = 'git'
pattern_test = re.compile(r'([\t]test/)|([\t]Test/)|([\t]tests/)|([\t]Tests/)|(/test/)|(/tests/)|(/Test/)|(/Tests/)|(-test/)|(-tests/)|(-Test/)|(-Tests/)|(_test/)|(_tests/)|(_Test/)|(_Tests/)|(test\.)|(tests\.)|(Test\.)(Tests\.)|(-test\.)|(-tests\.)|(-Test\.)(-Tests\.)|(/test\.)|(/tests\.)|(/Test\.)(/Tests\.)')

#pattern_test = re.compile(r'([\t]test/)|([\t]Test/)|([\t]tests/)|([\t]Tests/)')

def proc(cmd_args, pipe=True, dummy=False):
    if dummy:
        return
    if pipe:
        subproc = subprocess.Popen(cmd_args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    else:
        subproc = subprocess.Popen(cmd_args)
    return subproc.communicate()

def git(args, pipe=True):
    return proc([git_cmd] + args, pipe)

class Commit(object):
    def __init__(self,id,aut,date,megs,file,filetype):
        self.id = id
        self.aut = aut
        self.date = date
        self.megs = megs
        self.file = file
        self.filetype = filetype

    # 0表示满足要求，1表示不满足要求
    def condition_file(self):
        pattern_file = re.compile(r'(.\.doc$)|(.\.adoc$)|(.\.md$)|(.\.txt$)')
        #pattern_test = re.compile(r'(test/)|(tests/)|(Test/)|(Tests/)|(test\.)|(tests\.)|(Test\.)(Tests\.)')
        pattern_git = re.compile(r'(\.git$)|(\.gitignore$)|(\.travis$)')
        doc_num = 0
        key = 0
        for filet in self.file:
            if pattern_file.search(filet) != None :
                key = 1
                doc_num = doc_num + 1
            elif pattern_test.search(filet) != None :
                doc_num = doc_num +1
            elif pattern_git.search(filet) != None :
                doc_num = doc_num + 1
        if doc_num == len(self.file) and key == 1:
            return 0
        return 1

    def condition_git(self):
        #pattern_test = re.compile(r'(test/)|(tests/)|(Test/)|(Tests/)|(test\.)|(tests\.)|(Test\.)(Tests\.)')
        pattern_git = re.compile(r'(\.git$)|(\.gitignore$)|(\.travis)')
        doc_num = 0
        key = 0
        for filet in self.file:
            if pattern_git.search(filet) != None:
                key = 1
                doc_num = doc_num + 1
            elif pattern_test.search(filet) != None:
                doc_num = doc_num + 1
        if doc_num == len(self.file) and key == 1:
            return 0
        return 1

    def condition_test(self):
        #pattern_test = re.compile(r'(test/)|(tests/)|(Test/)|(Tests/)|(test\.)|(tests\.)|(Test\.)(Tests\.)')
        doc_num = 0
        key = 0
        for filet in self.file:
            if pattern_test.search(filet) != None:
                doc_num = doc_num + 1
        if doc_num == len(self.file) :
            return 0
        return 1

    def fixtyposearch(self):
        pattern_megs = re.compile(r'(fix typo)|(Fix typo)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def cvesearch(self):
        pattern_megs = re.compile(r'(cve)|(Cve)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def bugsearch(self):
        pattern_megs = re.compile(r'(bug)|(defect)|(error)|(Bug)|(Defect)|(Error)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def safesearch(self):
        pattern_megs = re.compile(r'(safe)|(safety)|(security)|(Safe)|(Safety)|(Security)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def fixsearch(self):
        pattern_megs = re.compile(r'(fix)|(Fix)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def addsearch(self):
        pattern_megs = re.compile(r'(add)|(Add)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def updatesearch(self):
        pattern_megs = re.compile(r'(update)|(upgrade)|(Update)|(Upgrade)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def removesearch(self):
        pattern_megs = re.compile(r'(delete)|(Delete)|(remove)|(Remove)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

    def renamesearch(self):
        pattern_megs = re.compile(r'(rename)|(Rename)')
        if pattern_megs.search(self.megs[0]) != None:
            return 0
        return 1

def print_obj(obj):
        print(obj.__dict__)

if __name__ == '__main__':

    git_name = sys.argv[1]
    branch_name = 'master'

    if len(sys.argv) > 2:
        opt = sys.argv[2]
        if opt == '-b':
            if len(sys.argv) > 3:
                branch_name = sys.argv[3]

    base_path=os.getcwd()
    git_path = base_path
    if str(git_name) != './':
        git_path=os.getcwd()+'/'+git_name
    # Switch path to git_path
    os.chdir(git_path)
    # Get git_name if git_name is './';
    if str(git_name) == './' :
        g_name = str(git_path).split('/')
        git_name = g_name[len(g_name)-1]

    git(['checkout',branch_name])

    git_commit = git(['log','--since=2018-11-13','--numstat'])
    git_com = git_commit[0].split('\ncommit ')
    num = 0
    blank,cfile ,cgit ,ctest ,cve ,safe ,bug ,other ,fix = [],[],[],[],[],[],[],[],[]
    fix2, add ,remove,rename,upgrade = [],[],[],[],[]
    for git_c in git_com:
        num = num + 1
        gg = git_c.split('\n')
        file = []
        file_name = []
        msg = []
        msg.append(gg[4])
        for i in range(6,len(gg)-1):
            if len(gg[i]) > 0 :
                fg = gg[i][0]
                if fg.isdigit():
                    file.append(gg[i])
                    file_n = gg[i].split('/')
                    fn = file_n[len(file_n)-1]
                    file_name.append(fn)
                else:
                    msg.append(gg[i])
        git_id = gg[0].split(' ')
        git_id2 = git_id[len(git_id)-1]
        c1 = Commit(git_id2,gg[1],gg[2],msg,file,file_name)
        if c1.filetype == []:
            blank.append(c1.id)
        elif c1.filetype != []:
            if c1.condition_file() == 0:
                cfile.append(c1.id)
            elif c1.condition_git() == 0:
                cgit.append(c1.id)
            elif c1.condition_test() == 0:
                ctest.append(c1.id)
            else :
                if c1.cvesearch() == 0:
                    cve.append(c1.id)
                elif c1.safesearch() == 0:
                    safe.append(c1.id)
                elif c1.bugsearch() == 0:
                    bug.append(c1.id)
                elif c1.fixtyposearch() == 0:
                    fix.append(c1.id)
                else:
                    other.append(c1.id)
                    if c1.fixsearch() == 0:
                        fix2.append(c1.id)
                    elif c1.addsearch() == 0:
                        add.append(c1.id)
                    elif c1.removesearch() == 0:
                        remove.append(c1.id)
                    elif c1.updatesearch() == 0:
                        upgrade.append(c1.id)
                    elif c1.renamesearch() == 0:
                        rename.append(c1.id)
    print("All commits is: ",num)
    print("********",num,"commits need remove following commits,including blank,document,git_file,test_file********")
    print("blank: ",len(blank),"\n",blank)
    print("\ndocument: ",len(cfile),"\n",cfile)
    print("\ngit_file: ",len(cgit),"\n",cgit)
    print("\ntest_file: ",len(ctest),"\n",ctest)

    print("\n********",num-len(blank)-len(cfile)-len(cgit)-len(ctest),"commits priority classification********")

    print("priority 1: cve ",len(cve))
    for c in cve:
        print("commitID:",c,"\tpriority type : cve")

    print("\npriority 2: safe ",len(safe))
    for s in safe:
        print("commitID:",s,"\tpriority type : safe")

    print("\npriority 3: bug ",len(bug))
    for b in bug:
        print("commitID:",b,"\tpriority type : bug")

    print("\npriority 4: others ", len(other)," , including \"fix\":",len(fix2),"\"add\":",len(add),"\"remove\":",len(remove),"\"upgrade\":",len(upgrade),"\"rename\":",len(rename),"\"other\":",len(other)-(len(fix2)+len(add)+len(rename)+len(remove)+len(upgrade)))

    print(" fix type in other:",fix2)
    print(" add type in other:",add)
    print(" remove type in other:",remove)
    print(" upgrade type in other:",upgrade)
    print(" rename type in other:",rename)

    print("\npriority 5: fix typo",len(fix))
    for f in fix:
        print("commitID:",f,"\tpriority type : fix typo")




