#! /usr/bin/env python
#
# ICPC challenge 2011 - Dejemeppe Cyrille & Mouthuy Francois-Xavier

import sys, getopt, commands, math, time, os

def one_play(player_1, player_2):
    out_play = commands.getoutput('java -jar ../icypc.jar -player pipe 2 python ' + player_1 + ' -player pipe 2 python ' + player_2 + ' -view trace tmp.txt')
    last_line = out_play.splitlines()[-1].split()
    p1_score = int(last_line[1])
    p2_score = int(last_line[4])
    p_hat = float(p1_score - p2_score)/(p1_score + p2_score)
    return p_hat

def k_fold(nb_plays, player_1, player_2, beg_time, verbose=False):
    p_bar = 0.0
    square_sum = 0.0
    p_hats = list()
    # Getting the results of the nb_plays plays
    for i in xrange(nb_plays):
        if verbose:
            print 'Playing play '+str(i+1)+' of '+str(nb_plays)+' (Total time elapsed: '+str(round(time.time()- beg_time,3))+' seconds)'
        p_hats.append(one_play(player_1, player_2))
        p_bar += p_hats[-1]
    p_bar /= nb_plays
    for p_hat in p_hats:
        square_sum += (p_hat - p_bar)**2
    sigma_p_bar = math.sqrt((1.0/(nb_plays - 1)) * square_sum)
    T = p_bar/(sigma_p_bar/math.sqrt(nb_plays))
    return T

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
    
    beg_time = time.time()
    t_025_inf = 1.96
    T = k_fold(nb_plays, args[0], args[1], beg_time, verbose)
    os.remove('tmp.txt')
    print '\n=====>>>>> Results computed in ' + str(round(time.time()-beg_time,3)) + ' seconds <<<<<=====\n'
    print '95% confidence interval:\n\tRR = [-inf; -1.96] U [1.96; inf]'
    print 'Test statistic:\n\tT = ' + str(round(T,3))
    if T < -1.96:
        print '\nWe accept, with 95% confidence, the hypothesis that the true performances are significantly different.'
        print 'And the best player is:\n\t\t', args[1]
    elif T > 1.96:
        print '\nWe accept, with 95% confidence, the hypothesis that the true performances are significantly different.'
        print 'And the best player is:\n\t\t', args[0]
    else:
        print '\nWe reject, with 95% confidence, the hypothesis that the true performances are significantly different.'
        print '\tThese two players are thus equivalent in terms of performances.'
    print '\n==========>>>>>>>>>> The end <<<<<<<<<<==========\n'
main()
