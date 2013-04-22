#!/usr/bin/env python
# Licensed under the terms of the GPL v3. See LICENCE for details

import sys
import getopt
import re

VERSION = "1.0"
REG = 10


# Convert functions
def stimetoms(stime):
    """stimetoms(stime)->mstime"""
    return ((stime[0] * 3600) + (stime[1] * 60) + stime[2]) * 1000 + stime[3]


def mstostime(mstime):
    """mstostime(mstime)->stime"""
    ms = mstime % 1000

    mstime /= 1000
    h = mstime / 3600
    mstime %= 3600
    m = mstime / 60
    mstime %= 60
    s = mstime

    return [h, m, s, ms]


# SubRip (srt) format functions
def convtime_srt(srttime):
    """convtime_srt(srttime)->stime"""
    h = srttime.split(":")
    m = h[-1:][0].split(",")
    time = h[:-1] + m
    ntime = list()
    for i in time:
        ntime.append(int(i))
    return ntime


def deconvtime_srt(stime):
    """deconvtime_srt(stime)->srttime"""
    return "%d:%d:%d,%d" % (stime[0], stime[1], stime[2], stime[3])


def loadsubs_srt(filename):
    """loadsubs_srt(filename)->subs
    Process srt format to subtitle structure"""
    if (filename != "-"):
        file = open(filename)
    else:
        file = sys.stdin
    s = list()
    data = ""
    oline = ""
    number = 0
    times = list()
    for line in file.xreadlines():
        line = line.strip()
        if ((line == "") and (oline == "")):
            continue
        if (line.isdigit() and (oline == "")):  # number of title (idle)
            number += 1
        elif (line.find("-->") != -1):
            times = line.split(" --> ")
            times[1] = times[1].split()[0]
        elif (line == ""):
            s.append([[stimetoms(convtime_srt(times[0])),
                    stimetoms(convtime_srt(times[1]))], data])
            data = ""
        else:
            data += line + "\n"
        oline = line
    file.close()
    return s


def printsubs_srt(subs):
    """printsubs_srt(subs)->None
    Print subtitle structure in srt format"""
    n = 1
    for i in subs:
        if (int(i[0][0]) >= 0 and int(i[0][1]) >= 0):
            print n
            print deconvtime_srt(mstostime(i[0][0])), "-->",\
                  deconvtime_srt(mstostime(i[0][1]))
            print i[1]
            n += 1


# MicroDVD (sub) format functions
def fpstostime(fpstime, fps):
    """fpstostime(fpstime,fps)->stime"""
    t = fpstime / fps / 1.0
    h = int(t / 3600)
    t = t % 3600
    m = int(t / 60)
    t = t % 60
    s = int(t)
    ms = int((t - s) * 1000)
    return [h, m, s, ms]


def stimetofps(stime, fps):
    return ((stime[0] * 3600) + (stime[1] * 60) +
            stime[2] + (stime[3] / 1000)) * fps


def loadsubs_sub(filename, fps):
    """loadsubs_sub(filename,fps)->subs
    Process sub format to subtitle structure"""
    if (filename != "-"):
        file = open(filename)
    else:
        file = sys.stdin
    s = list()
    data = ""
    number = 1
    for line in file.xreadlines():
        if (line.strip() == ""):
            continue
        data = re.sub(r'{([0-9]*)}{([0-9]*)}(.*)', r'\1|\2|\3',\
                re.sub(r'\|', r'\n', line)).split("|")
        s.append([[stimetoms(fpstostime(int(data[0]), fps)),\
                stimetoms(fpstostime(int(data[1]), fps))],\
                "".join(data[2:]).replace("|", "\n")])
        number += 1
    return s


def printsubs_sub(subs, fps):
    """printsubs_sub(subs,fps)->None
    Print subtitle structure in sub format"""
    print "{0}{1}%f" % (fps)
    for i in subs:
        if (int(i[0][0]) >= 0 and int(i[0][1]) >= 0):
            print "{%d}{%d}%s" % (stimetofps(mstostime(i[0][0]), fps),
                    stimetofps(mstostime(i[0][1]), fps),
                    "".join(i[1:]).replace("\n", "|")[:-1])


# Common functions
# ################
def printhelp():
    print "Ussage:", sys.argv[0].split('/')[-1:][0],\
          " [-t s] [-s i] [-i s[:f]] [-o s[:f]] [-h] [-v] [file]"
    print " -t [shifttime] - Seek times. '[+-]h:m:s,ms'"
    print " -s [number]    - Left limit of part to shift"
    print " -i [format]    - Input format (srt,sub:fps)"
    print " -o [format]    - Output format (srt,sub:fps)"
    print " -h             - Help"
    print " -v             - Version"

    sys.exit(0)


def printversion():
    print "Version:", VERSION
    sys.exit(0)


def shiftsubs(subs, time):
    """shiftsubs(subs,shifttime)->subs"""
    way = 1
    if (time[0] == "-"):
        way = 0
    if (len(subs) > 0):
        if (way):
            subs[0][0][0] += stimetoms(convtime_srt(time[1:]))
            subs[0][0][1] += stimetoms(convtime_srt(time[1:]))
        else:
            subs[0][0][0] -= stimetoms(convtime_srt(time[1:]))
            subs[0][0][1] -= stimetoms(convtime_srt(time[1:]))
        shiftsubs(subs[1:], time)  # Let's give it a twist!
    return subs

# Getting options
ok = 1
try:
    opts, args = getopt.getopt(sys.argv[1:], "t:s:i:o:hv",\
                    ["time=", "sub=", "input=", "output=", "help", "version"])
except getopt.error:
    ok = 0

opt_t = "+0:0:0,0"
opt_s = 1
opt_i = "srt"
opt_o = "srt"
for opt, arg in opts:
    if (opt in ('-t', '--time')):
        if (arg[0] in ('+', '-')):
            opt_t = arg
        else:
            print >>sys.stderr, "Time format: +h:m:s,ms or -h:m:s,ms"
            sys.exit(2)
    if (opt in ('-s', '--sub')):
        if (arg.isdigit()):
            opt_s = arg
        else:
            print >>sys.stderr, "Bad number of title:", arg
            sys.exit(5)
    if (opt in ('-i', '--input')):
        opt_i = arg
        opt_o = arg
    if (opt in ('-o', '--output')):
        opt_o = arg
    if (opt in ('-h', '--help')):
        printhelp()
    if (opt in ('-v', '--version')):
        printversion()

i = int(opt_s)
shifttime = opt_t
if (len(args) < 1):
    filename = "-"
else:
    filename = args[0]

if (opt_i == "srt"):
    subs = loadsubs_srt(filename)
elif (opt_i.split(":")[0] == "sub"):
    if (len(opt_i.split(":")) > 1):
        fps = opt_i.split(":")[1]
        subs = loadsubs_sub(filename, float(fps))
    else:
        print >>sys.stderr, "You must enter a fps with sub format!"
        sys.exit(3)
else:
    print >>sys.stderr, "Supported formats: srt, sub:fps"
    sys.exit(4)


sys.setrecursionlimit(len(subs) + REG)

subs = subs[:i - 1] + shiftsubs(subs[i - 1:], shifttime)

if (opt_o == "srt"):
    printsubs_srt(subs)
    sys.exit(0)
elif (opt_o.split(":")[0] == "sub"):
    if (len(opt_o.split(":")) > 1):
        fps = opt_o.split(":")[1]
        printsubs_sub(subs, float(fps))
    else:
        print >>sys.stderr, "You must enter a fps with sub format!"
        sys.exit(3)
else:
    print >>sys.stderr, "Supported formats: srt, sub:fps"
    sys.exit(4)
