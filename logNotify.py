#!/usr/bin/env python
# 
# Original Date: 05-30-2019
#
# Blame: Colton22
#
# Script: logNotify.py
# Description: Search for keywords in files
version = "v1.1"
changelog = """
Version: v1.1
    - Fixed python not waiting for email to send before deleting file
Version: v1.0
    - First Version of Script
    - Started Changelog
"""

#####
# Criteria
# !!! MUST EDIT THIS SECTION !!!
#####
search_criteria = [ 'ERROR','secondterm' ]
watch_dir = '/var/log/'
file_extentions = [ 'log' ]

#####
# Globals
# !!! These are systematically updated !!!
#####
quiet = False
basic = False
showLines = False
showLineNumber = False
email_to = ''
send_email = True
tmpFile = '/tmp/logNotify_'+watch_dir.encode('base64').strip('=').strip()
createdFiles = []
modules = [ 'sys', 'os', 'subprocess' ]

#####
# Set Color Options
#####
class fg:
        BLACK   = '\033[30m'
        RED     = '\033[31m'
        GREEN   = '\033[32m'
        YELLOW  = '\033[33m'
        BLUE    = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN    = '\033[36m'
        WHITE   = '\033[37m'
        RESET   = '\033[39m'

class bg:
        BLACK   = '\033[40m'
        RED     = '\033[41m'
        GREEN   = '\033[42m'
        YELLOW  = '\033[43m'
        BLUE    = '\033[44m'
        MAGENTA = '\033[45m'
        CYAN    = '\033[46m'
        WHITE   = '\033[47m'
        RESET   = '\033[49m'

class style:
        BRIGHT    = '\033[1m'
        DIM       = '\033[2m'
        UNDERLINE = '\033[4m'
        NORMAL    = '\033[22m'
        RESET_ALL = '\033[0m'

#####
# load_module Function
#   - mod     |  Module to import      |  string  |  REQUIRED
#  return bool; Safe Loading of Modules with error checking
#####
def load_module(mod):
    try:
        globals()[mod] = __import__(mod)
        return True
    except:
        return False
#####
# Catch Ctrl + C
#####
def signal_handler(sig, frame):
    cleanExit("User Aborted using Ctrl+C")

#####
# colors Function
#  remove coloring if running via ansible
#####
def colors(t,c,isfile = False):
    if arg_index('--nocolor') or isfile:
        return ''
    else:
        return eval(t+'.'+c)

#####
# showVersion Function
#  Shows current Script Version and full changelog with --all
#####
def showVersion():
    print('\n'+colors('fg','YELLOW')+colors('style','BRIGHT')+colors('style','UNDERLINE')+'logNotify - Tool to monitor for patterns in files'+colors('style','RESET_ALL'))
    print('  Written by: '+colors('style','UNDERLINE')+'Colton22'+colors('style','RESET_ALL'))
    print('  Version: '+colors('style','UNDERLINE')+version+colors('style','RESET_ALL'))
    print('  GitHub: '+colors('fg','CYAN')+colors('style','BRIGHT')+colors('style','UNDERLINE')+'https://github.com/colton22/logNotify'+colors('style','RESET_ALL'))
    print('  ChangeLog (use --all to view all)')
    if arg_index('--all'):
        for l in changelog.split('\n'):
            if not l.strip() == '':
                print('    '+l)
    else:
        for l in changelog.split('Version: ')[1].split('\n'):
            if not l.strip() == '':
                print('    '+l)
    print('')
    cleanExit()

#####
# showHelp Function
#   - full  |  Show Full Help Menu  |  bool  | OPTIONAL
#  Show Help Menu, Then Exit. (Defaults to mini menu)
#####
def showHelp(full = False,msg = ''):
    if msg != '':
        print(msg)
    if full:
        print('Usage:')
        print('  logNotify.py [FLAGS]')
        print('\nOptional Flags:')
        print('  -e, --email     Email Recipent of Report')
        print('  -q, --quiet     Do not show anything on screen')
        print('  -b, --basic     Show Basic Information on Matches')
        print('  -l, --lines     Show Full Lines that Match')
        print('  -n, --num       Show Line Numbers that Match')
        print('  -h, --help      Show this Help Menu')
        print('      --noemail   Do Not Send Email')
        print('      --version   Show Version Information')
        print('      --no/color  Show/Dont show colored output')
    else:
        print('  Usage: logNotify.py [--help] [--email (address)] [--quiet/basic/lines/num] [--noemail]\n')
    cleanExit()

#####
# arg_index Function
#   - arg   |  index to look for  |  string  |  REQUIRED
#   - args  |  list of arguments  |  array   |  OPTIONAL
#  Retrieve Arguments Postion from sys.argv with error checking
#####
def arg_index(arg,args = []):
    if args == []:
        args = sys.argv
    largs = [x.lower() for x in args]
    try:
        return largs.index(arg)
    except:
        return 0

#####
# arg_value Function
#   - arg   |  index to look for  |  string  |  REQUIRED
#   - args  |  list of arguments  |  array   |  OPTIONAL
#  Retrieve Argument Value
#####
def arg_value(arg,args = []):
    if args == []:
        args = sys.argv
    try:
        return args[arg_index(arg,args)+1]
    except:
        return ''

#####
# rFile Function
#   - filename  |  Name of file to read  |  string  |  REQUIRED
#  returns string or None
#####
def rFile(filename):
    try:
        handle = open(filename,'r')
        cont = handle.read()
        handle.close()
        return cont
    except:
        return None

#####
# wFile Function
#   - filename  |  Name of file to write   |  string  |  REQUIRED
#   - contents  |  File Contents to write  |  string  |  REQUIRED
#   - method    |  File open method        |  string  |  OPTIONAL
#  returns bool
#####
def wFile(filename, contents, method = 'a'):
#    try:
    handle = open(filename,method)
    handle.write(contents)
    handle.close()
    return True
#    except:
#        return False

#####
# cleanExit Function
#   - msg     |  Message to show          |  string  |  OPTIONAL
#   - ErrLvl  |  Define Exit Error Level  |  int     |  OPTIONAL
#  show msg if defined, set error level and exit
#####
def cleanExit(msg = '', ErrLvl = 0):
    global createdFiles
    if len(createdFiles) > 0:
        lf = len(createdFiles) - 1
        while lf >= 0:
            try:
                os.remove(createdFiles[lf])
            except:
                print('error remvoing file '+lf)
                pass
            lf = lf - 1
    if msg != '':
        print(msg)
    try:
        sys.exit(ErrLvl)
    except:
        quit()

#####
# parseArgs Function
#####
def parseArgs():
    global email_to, quiet, basic, showLines, showLineNumber, send_email
    if arg_index('--help') or arg_index('-h'):
        showHelp(True)
    if arg_index('--version'):
        showVersion()
    if arg_index('--lines') or arg_index('-l'):
        showLines = True
    if arg_index('--quiet') or arg_index('-q'):
        quiet = True
    if arg_index('--basic') or arg_index('-b'):
        basic = True
    if arg_index('--num') or arg_index('-n'):
        showLineNumber = True
    if arg_index('--noemail'):
        send_email = False
    if arg_index('-e') or arg_index('--email'):
        if not send_email:
            showHelp(msg='You specified both --email and --noemail')
        email_to = arg_value('-e') if arg_index('--email') == 0 else arg_value('--email')
        if email_to == '': showHelp(msg='Please Specify an email address!')
        if '@' not in email_to: showHelp(msg='Invalid email address!')

#####
# getDifferences Function
#####
def getDifferences(old,new):
    if old == None:
        old = ''
    diff = []
    for line in new.split('\n'):
        if line not in old:
            diff.append(line)
    return diff

#####
# Main Function
#####
def main():
    global email_to, showLines, showLineNumber, search_criteria, \
           watch_dir, file_extentions, tmpFile, createdFiles, modules
    for mod in modules:
        if not load_module(mod):
            cleanExit('You are missing the required python2 modules! I need: '+', '.join(modules),1)
    if len(sys.argv) == 1:
       showHelp(msg='You must have at least one parameter to run this script')
    parseArgs()
    msg = ''        
    files_to_check = []
    for f in os.listdir(watch_dir):
        if f.split('.')[ len(f.split('.')) - 1 ] in file_extentions:
            files_to_check.append(f)
    for log in files_to_check:
        log_contents = rFile(watch_dir + log)
        for term in search_criteria:
            if term in log_contents:
                if showLineNumber or showLines:
                    count = 0
                    for line in log_contents.split('\n'):
                        count = count + 1
                        if term in line:
                            if not showLines:
                                msg = msg + 'Found ' + term + ' in ' + log + ':'+str(count) + '\n'
                            else:
                                msg = msg + log+':'+str(count)+' | '+line + '\n'
                else:
                    msg = msg + 'Found |' + term + '| ' + str(log_contents.count(term)) + ' times in ' + log + '\n'
    if showLines:
        tmpFile=tmpFile + 'l.txt'
    elif showLineNumber:
        tmpFile=tmpFile + 'n.txt'
    else:
        tmpFile=tmpFile + 'b.txt'
    prior = rFile(tmpFile)
    wFile(tmpFile,msg,'w')
    diff = '\n'.join(getDifferences(prior,rFile(tmpFile)))
    wFile(tmpFile+'.tmp',diff,'w')
    createdFiles.append(tmpFile+'.tmp')
    if send_email:
        if email_to == '':
            showHelp(False,'You did not supply an email address!')
        if not quiet:
            if diff.strip() == '':
                print('No Differences!')
            else:
                print(diff)
        if not diff.strip() == '':
            print(repr(diff.strip()))
            email = subprocess.call('cat '+tmpFile+'.tmp | /usr/bin/mail '+email_to, shell=True)
            
    else:
        if quiet: 
            cleanExit('You gave me no output options!',1)
        if diff.strip() == '':
            print('No Differences!')
        else:
            print(diff)
    cleanExit()

if __name__ == '__main__':
    main()
