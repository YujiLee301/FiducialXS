import ROOT
import sys, os, pwd, commands
from subprocess import *
import optparse, shlex, re
import math
import time
from decimal import *
import json

from higgs_xsbr_13TeV import *
from read_bins import *

def parseOptions():

    global opt, args, runAllSteps

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-d', '--dir',      dest='SOURCEDIR',type='string',default='./', help='run from the SOURCEDIR as working area, skip if SOURCEDIR is an empty string')
    parser.add_option('',   '--theoryMass',dest='THEORYMASS',    type='string',default='125.38',   help='Mass value for theory prediction')
    parser.add_option('',   '--obsName',  dest='OBSNAME',  type='string',default='mass4l',   help='Name of the observable, supported: "inclusive", "pT4l", "eta4l", "massZ2", "nJets"')
    parser.add_option('',   '--obsBins',  dest='OBSBINS',  type='string',default='|105|160|',   help='Name of the observable, supported: "inclusive", "pT4l", "eta4l", "massZ2", "nJets"')  
    parser.add_option('',   '--year',  dest='YEAR',  type='string',default='2018',   help='Year -> 2016 or 2017 or 2018 or allYear')
    parser.add_option('',   '--doHIG', action='store_true', dest='DOHIG', default=False, help='use HIG 19 001 acceptances')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()



# parse the arguments and options
global opt, args
parseOptions()

def exp_xs():
    # prepare the set of bin boundaries to run over, only 1 bin in case of the inclusive measurement
    observableBins_string = opt.OBSBINS
    observableBins = read_bins(observableBins_string)
    doubleDiff = False
    if doubleDiff:
        obs_name = opt.OBSNAME.split(' vs ')[0]
        obs_name_2nd = opt.OBSNAME.split(' vs ')[1]
        obs_name_2d = opt.OBSNAME
        doubleDiff = True
    else:
        obs_name = opt.OBSNAME
        doubleDiff = False
    ## Run for the given observable
    # obsName = opt.OBSNAME
    if doubleDiff: obsName = obs_name+'_'+obs_name_2nd
    else: obsName = obs_name
    _th_MH = opt.THEORYMASS
    print 'Running Fiducial XS computation - '+obsName+' - bin boundaries: ', observableBins, '\n'
    print 'Theory xsec and BR at MH = '+_th_MH

    _temp = __import__('higgs_xsbr_13TeV', globals(), locals(), ['higgs_xs','higgs4l_br'], -1)
    higgs_xs = _temp.higgs_xs
    higgs4l_br = _temp.higgs4l_br
    fname = 'inputs_sig_'+obsName
    
    if opt.DOHIG: fname = fname + '_HIG19001'
    print("Importing: " + str(fname))
    os.system('cp datacardInputs/'+opt.YEAR+'/'+fname+'.py python/'+fname+'.py')

    _temp = __import__(fname, globals(), locals(), ['acc'], -1)
    acc = _temp.acc
    XH = []
    nBins = len(observableBins)
    if not doubleDiff: nBins = nBins - 1
    xs = {}
    for obsBin in range(nBins):
        XH.append(0.0)
        # if('mass4l' not in obsName):
        for channel in ['4e','4mu','2e2mu']:
            XH_fs = higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ggH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
            XH_fs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['VBF_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
            XH_fs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['WH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
            XH_fs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ZH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
            XH_fs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ttH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
 
            print 'Bin ', obsBin, '\t SigmaBin', obsBin, channel, ' = ', XH_fs
            XH[obsBin]+=XH_fs


        _obsxsec = XH[obsBin]

        print '\n'
        print 'Bin ', obsBin, '\t SigmaBin', obsBin, ' = ', _obsxsec
        xs['SigmaBin'+str(obsBin)] = _obsxsec

    with open('./Inputs/xsec_'+obsName+'.py', 'w') as f:
        f.write('xsec = '+str(xs)+' \n')

exp_xs()