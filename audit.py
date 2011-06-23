#!/usr/bin/env python

import os
import shutil
import subprocess
import pickle
from tempfile import mkdtemp
from urllib2 import urlopen
from re import compile, match

def run(options):
    '''takes a list containing shell command and options'''
    process = subprocess.Popen(options, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    return process


if not os.path.exists('.cache'):
    all_requires = {}

    u = urlopen('http://dl.iuscommunity.org/pub/ius/stable/Redhat/5/SRPMS/')
    req = u.read()
    pkgs = compile('href="(.*.src.rpm)">').findall(req)

    for srpm in pkgs:
        url = 'http://dl.iuscommunity.org/pub/ius/stable/Redhat/5/SRPMS/%s' % srpm

        print 'Getting Requirements for %s' % srpm
        rpm = run(['rpm', '-qp', url, '--requires'])
        requires = rpm.communicate()[0].split('\n')
        for i in requires:
            req = i.lstrip()
            req = req.split()
            if len(req) >= 1:
                req = req[0]
            else:
                continue

            all_requires[req] = True

    # write cache 
    f = open('.cache', 'wb')
    pickle.dump(all_requires, f)
else:
    f = open('.cache', 'rb')
    all_requires = pickle.load(f)


for pkg in sorted(all_requires):
    rpm = run(['yum', 'info', pkg])
    match = compile('Repo(.*)').findall(rpm.communicate()[0])

    # remove duplicates
    match = list(set(match))

    for m in match:
        if 'epel' in m:
            print '%-18s%s' % (pkg, m)
