#! /usr/bin/env python
#
# ICPC challenge 2011 - Dejemeppe Cyrille & Mouthuy Francois-Xavier

import sys, getopt

def one_play():
    print 'I love Jesus'

def default_usage():
    """The function used when program launched with wrong arguments"""
    print 'default usage:'
    print '\t', sys.argv[0], '[options]', 'first_player', 'second_player'
    print 'options:'
    print '\t-v, --verbose\n\t\tprint the number of iteration for every game'
    print '\t-n num, --nb_plays num\n\t\tset the number of plays to num'
    sys.exit(1)

def main():
    nb_plays = 100
    verbose = False
    
    # Separates the command line in arguments and options
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'n:v', ['nb_plays=', 'verbose'])

    # Checks if the script was given two arguments
    if len(args) != 2:
        default_usage()

    # Treats the options
    for op, ar in opts:
        if op in ('-v', '--verbose'):
            verbose = True
        elif op in ('-n', '--nb_plays'):
            try:
                nb_plays = int(ar)
            except:
                default_usage()
    
    print '--verbose:', verbose
    print '--nb_plays', nb_plays

main()
