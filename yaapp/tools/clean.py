#!/usr/bin/python
# This command line tool reencodes all the mp3s files in the given folder tree at 192 kbps CBR (while skipping the previews)
# It works in place so beware!
import os, sys
import subprocess
import re

lamepath = '/usr/bin/lame'
total = 0
ok = 0
nok = 0
path = os.getcwdu()
for root, dirs, files in os.walk(path):
    #print root
    #for d in dirs:
        #print '\t==> ' + d
    for f in files:
        #print '\t--> ' + f
	p, e = os.path.splitext(f)
	if p[3:11] != '_preview':
            input = os.path.join(root, f)
            #process = subprocess.Popen('/usr/bin/mp3info -x "%s"'%input, stdout=subprocess.PIPE)
            process = subprocess.Popen(['/usr/bin/mp3info', '-x', input], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            poutput, errors = process.communicate()
            lines = poutput.splitlines()
            done = False
            total = total + 1
            for i in lines:
                if (re.match('^Audio', i) != None)  & (i != 'Audio:       192 kbps, 44 kHz (joint stereo)'):
                    done = True
            if done == False:
                print 'skiping ' + input
                ok = ok + 1
            else:
                output = input + '_tmp'
                nok = nok + 1
                print "re encoding " + input + '  [' + i + ']'#+ '\t--> ' + output
                res = subprocess.call([lamepath, '-S', '-cbr', '-b 192', '-q 2', '-h', input, output])
                if res == 0:
                    subprocess.call(["mv", '-f', output, input])

print "Results\nTotal:\t" + str(total) + '\nOk:\t' + str(ok) + '\nNot ok:\t' + str(nok) + '\n'
