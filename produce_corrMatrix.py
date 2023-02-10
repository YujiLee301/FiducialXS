import ROOT
import sys, os, pwd
from subprocess import *
import optparse, shlex, re
import math
import time
from decimal import *
import json
from collections import OrderedDict as od
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Utils import processCmd


from read_bins import *
import yaml


from higgs_xsbr_13TeV import *

def parseOptions():

    global opt, args, runAllSteps

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('',   '--theoryMass',dest='THEORYMASS',    type='string',default='125.38',   help='Mass value for theory prediction')
    parser.add_option('',   '--obsName',  dest='OBSNAME',  type='string',default='pT4l',   help='Name of the observable, supported: "inclusive", "pT4l", "eta4l", "massZ2", "nJets"')
    parser.add_option('',   '--obsBins',  dest='OBSBINS',  type='string',default='|0|10|20|30|45|60|80|120|200|13000|',   help='Bin boundaries for the diff. measurement separated by "|", e.g. as "|0|50|100|", use the defalut if empty string')
    parser.add_option('',   '--unblind', action='store_true', dest='UNBLIND', default=False, help='Use real data')
    parser.add_option('',   '--inYAMLFile', dest='inYAMLFile', type='string', default="Inputs/observables_list.yml", help='Input YAML file having observable names and bin information')
    parser.add_option('', '--bkg',      dest='BKG',type='string',default='', help='run with the type of zz background to float zz or qq_gg ')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()

# parse the arguments and options
parseOptions()

def RunCombineCorrelation():


    for physicalModel in PhysicalModels:
        if physicalModel == 'v2': # In this case implemented for mass4l only
	    if (opt.BKG==''):
                cmd = 'combine -n _'+obsName+'_'+physicalModel+' -M MultiDimFit combine_files/SM_125_all_13TeV_xs_'+obsName+'_bin_v2.root -m 125.38 --freezeParameters MH --floatOtherPOIs=1 --saveWorkspace --setParameterRanges r4eBin0=0.0,2.5:r4muBin0=0.0,2.5:r2e2muBin0=0.0,2.5 --redefineSignalPOI r4eBin0,r4muBin0,r2e2muBin0 --algo=singles --cminDefaultMinimizerStrategy 0 --saveInactivePOI=1 --robustHesse 1 --robustHesseSave 1'
            if (opt.BKG!=''):
                if (opt.BKG=='zz'): 
		    cmd = 'combine -n _'+obsName+'_'+physicalModel+opt.BKG+' -M MultiDimFit combine_files/SM_125_all_13TeV_xs_'+obsName+'_bin_v2'+opt.BKG+'.root -m 125.38 --freezeParameters MH --floatOtherPOIs=1 --saveWorkspace --setParameterRanges r4eBin0=0.0,2.5:r4muBin0=0.0,2.5:r2e2muBin0=0.0,2.5:zz_norm_0=0.0,1000.0 --redefineSignalPOI r4eBin0,r4muBin0,r2e2muBin0,zz_norm_0 --algo=singles --cminDefaultMinimizerStrategy 0 --saveInactivePOI=1 --robustHesse 1 --robustHesseSave 1'

                if (opt.BKG=='zz_chan'): 
		    cmd = 'combine -n _'+obsName+'_'+physicalModel+opt.BKG+' -M MultiDimFit combine_files/SM_125_all_13TeV_xs_'+obsName+'_bin_v2'+opt.BKG+'.root -m 125.38 --freezeParameters MH --floatOtherPOIs=1 --saveWorkspace --setParameterRanges r4eBin0=0.0,2.5:r4muBin0=0.0,2.5:r2e2muBin0=0.0,2.5:zz_norm_2e2mu=0.0,2.0:zz_norm_4mu=0.0,2.0:zz_norm_4e=0.0,2.0 --redefineSignalPOI r4eBin0,r4muBin0,r2e2muBin0,zz_norm_2e2mu,zz_norm_4mu,zz_norm_4e --algo=singles --cminDefaultMinimizerStrategy 0 --saveInactivePOI=1 --robustHesse 1 --robustHesseSave 1'


            if not opt.UNBLIND:
                cmd += ' -t -1 --setParameters '
                for channel in ['4e', '4mu', '2e2mu']:
                    fidxs = 0
                    fidxs = higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ggH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin0_recobin0']
                    fidxs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['VBF_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin0_recobin0']
                    fidxs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['WH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin0_recobin0']
                    fidxs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ZH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin0_recobin0']
                    fidxs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ttH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin0_recobin0']
                    cmd += 'r'+channel+'Bin0='+str(round(fidxs,4))+','
                cmd = cmd[:-1]



            print cmd, '\n'
            output = processCmd(cmd)

        if physicalModel == 'v4':
            # ----- 2e2mu -----
            cmd = 'combine -n _'+obsName+'_'+physicalModel+' -M MultiDimFit combine_files/SM_125_all_13TeV_xs_'+obsName+'_bin_v4.root -m 125.38 --freezeParameters MH --floatOtherPOIs=1 --saveWorkspace --algo=singles --cminDefaultMinimizerStrategy 0 --saveInactivePOI=1 --robustHesse 1 --robustHesseSave 1 --setParameterRanges '

            for obsBin in range(nBins):
                cmd += 'r2e2muBin'+str(obsBin)+'=0.0,2.5:r4lBin'+str(obsBin)+'=0.0,2.5:'

            cmd = cmd[:-1]
            cmd += ' --redefineSignalPOI '

            for obsBin in range(nBins):
                cmd += 'r2e2muBin'+str(obsBin)+',r4lBin'+str(obsBin)+','
            cmd = cmd[:-1]

            if not opt.UNBLIND:
                cmd += ' -t -1 --setParameters '
                for obsBin in range(nBins):
                    fidxs = 0
                    fidxs = higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_2e2mu']*acc['ggH_powheg_JHUgen_125.38_2e2mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_2e2mu']*acc['VBF_powheg_JHUgen_125_2e2mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_2e2mu']*acc['WH_powheg_JHUgen_125_2e2mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_2e2mu']*acc['ZH_powheg_JHUgen_125_2e2mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_2e2mu']*acc['ttH_powheg_JHUgen_125_2e2mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    if(not opt.UNBLIND): cmd += 'r2e2muBin'+str(obsBin)+'='+str(round(fidxs,4))+','

                    fidxs = 0
                    # 4e
                    fidxs = higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4e']*acc['ggH_powheg_JHUgen_125.38_4e_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4e']*acc['VBF_powheg_JHUgen_125_4e_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4e']*acc['WH_powheg_JHUgen_125_4e_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4e']*acc['ZH_powheg_JHUgen_125_4e_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4e']*acc['ttH_powheg_JHUgen_125_4e_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    # 4mu
                    fidxs += higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4mu']*acc['ggH_powheg_JHUgen_125.38_4mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4mu']*acc['VBF_powheg_JHUgen_125_4mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4mu']*acc['WH_powheg_JHUgen_125_4mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4mu']*acc['ZH_powheg_JHUgen_125_4mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    fidxs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_4mu']*acc['ttH_powheg_JHUgen_125_4mu_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    if(not opt.UNBLIND): cmd += 'r4lBin'+str(obsBin)+'='+str(round(fidxs,4))+','
                cmd = cmd[:-1]

            print cmd, '\n'
            output = processCmd(cmd)


        elif physicalModel == 'v3':

            cmd = 'combine -n _'+obsName+'_'+physicalModel+opt.BKG+' -M MultiDimFit combine_files/SM_125_all_13TeV_xs_'+obsName+'_bin_v3'+opt.BKG+'.root -m 125.38 --freezeParameters MH --floatOtherPOIs=1 --saveWorkspace --algo=singles --cminDefaultMinimizerStrategy 0 --robustHesse 1 --robustHesseSave 1 --setParameterRanges '
            for obsBin in range(nBins):
                cmd += 'r_smH_SM_125_'+str(obsBin)+'=0.0,2.5:'

	    if (opt.BKG!=''):
		if (opt.BKG=='zz'): cmd += 'zz_norm_0=0.0,1000.0'
		if (opt.BKG=='zz_chan'): cmd += 'zz_norm_2e2mu=0.0,2.0:zz_norm_4mu=0.0,2.0:zz_norm_4e=0.0,2.0'
	    else: cmd = cmd[:-1]

            cmd += ' --redefineSignalPOI '
            for obsBin in range(nBins):
                cmd += 'r_smH_SM_125_'+str(obsBin)+','
            cmd = cmd[:-1]
            if (opt.BKG!=''):
                if (opt.BKG=='zz'): cmd += ',zz_norm_0'
                if (opt.BKG=='zz_chan'): cmd += ',zz_norm_2e2mu,zz_norm_4mu,zz_norm_4e'

            if not opt.UNBLIND:
                cmd += ' -t -1 --setParameters '
#                XH = []
                for obsBin in range(nBins):
                    # XH.append(0.0)
                    # for channel in ['4e','4mu','2e2mu']:
                    #     XH_fs = higgs_xs['ggH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ggH_powheg_JHUgen_125.38_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    #     XH_fs += higgs_xs['VBF_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['VBF_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    #     XH_fs += higgs_xs['WH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['WH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    #     XH_fs += higgs_xs['ZH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ZH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    #     XH_fs += higgs_xs['ttH_'+opt.THEORYMASS]*higgs4l_br[opt.THEORYMASS+'_'+channel]*acc['ttH_powheg_JHUgen_125_'+channel+'_'+obsName+'_genbin'+str(obsBin)+'_recobin'+str(obsBin)]
                    #     XH[obsBin]+=XH_fs

                    if(obsName!='mass4l'): cmd += 'r_smH_SM_125_'+str(obsBin)+'=1,' 
                    if(obsName=='mass4l'): cmd += 'SigmaBin'+str(obsBin)+'=2.86,'
                cmd = cmd[:-1]
            print cmd, '\n'
            output = processCmd(cmd)

        processCmd('mv robustHesse_'+obsName+'_'+physicalModel+opt.BKG+'.root xs_125.0_allYear/') # wanted combine output
        processCmd('rm higgsCombine_'+obsName+'_'+physicalModel+'.MultiDimFit.mH'+opt.THEORYMASS+'.root') # unwanted combine output
        processCmd('rm combine_logger.out') # unwanted combine output

def PlotCorrelation():
    for physicalModel in PhysicalModels:
        pois = []
        pois_plot = []
        if obsName=='mass4l' and physicalModel == 'v2':
            pois = ['r4muBin0', 'r4eBin0', 'r2e2muBin0']
            pois_plot = ['$\sigma_{4\mu}$', '$\sigma_{4e}$', '$\sigma_{2e2\mu}$']
	    if(opt.BKG!=''):
		if(opt.BKG=='zz'):
		    pois += ['zz_norm_0']
		    pois_plot += ['ZZ']
		elif(opt.BKG=='zz_chan'):
		    pois += ['zz_norm_2e2mu','zz_norm_4mu','zz_norm_4e']
		    pois_plot += ['$zz_norm_{2e2\mu}$','$zz_norm_{4\mu}$','$zz_norm_{4e}$']
        elif physicalModel == 'v4':
            for obsBin in range(nBins):
                pois += ['r4lBin'+str(obsBin)]
                pois_plot += ['$\sigma_{4e+4\mu,'+str(obsBin)+'}$']
            for obsBin in range(nBins):
                pois += ['r2e2muBin'+str(obsBin)]
                pois_plot += ['$\sigma_{2e2\mu,'+str(obsBin+1)+'}$']
        else:  # v3
            for obsBin in range(nBins):
                pois += ['r_smH_SM_125_'+str(obsBin)]
                pois_plot += ['$\sigma^{fid}_{bin'+str(obsBin)+'}$']
            if (obsName == 'mass4l' and opt.BKG!=''):
	        if(opt.BKG=='zz'):
                    pois += ['zz_norm_0']
                    pois_plot += ['ZZ']
                elif(opt.BKG=='zz_chan'):
                    pois += ['zz_norm_2e2mu','zz_norm_4mu','zz_norm_4e']
                    pois_plot += ['$zz_norm_{2e2\mu}$','$zz_norm_{4\mu}$','$zz_norm_{4e}$']


        pars = od()
        inFile    = ROOT.TFile('xs_125.0_allYear/robustHesse_'+obsName+'_'+physicalModel+opt.BKG+'.root','READ')
        theMatrix = inFile.Get('h_correlation')
        theList   = inFile.Get('floatParsFinal')
        print "theList:  ", theList
        for iPar in range(len(theList)):
            print( theList[iPar].GetName() )
            if not (theList[iPar].GetName() in pois): continue
            print(iPar, theList[iPar])
            pars[theList[iPar].GetName()] = iPar

        nPars = len(pars.keys())
        print ('Procesing the following %g parameters:'%nPars)
        for par in pars.keys(): print (par)
        revPars = {i:name for name,i in pars.items()}
        # theHist = ROOT.TH2F('corr', '', nPars, -0.5, nPars-0.5, nPars, -0.5, nPars-0.5)
        theMap = {}
        for iBin,iPar in enumerate(pars.values()):
            for jBin,jPar in enumerate(pars.values()):
                proc = theMatrix.GetXaxis().GetBinLabel(iPar+1)
                theVal = theMatrix.GetBinContent(iPar+1,jPar+1)
                theMap[(revPars[iPar],revPars[jPar])] = theVal

        rows = []
        for i in pois:
            row = []
            for j in pois:
                row.append(theMap[(i,j)])
            rows.append(row)
        #for b in pois:
         #   rows.append([theMap[i] for i in theMap if i[0]==b])

        theMap = pd.DataFrame(rows, pois_plot, pois_plot)
        print(theMap)

        fig, ax = plt.subplots(figsize = (20, 10))
        ax.text(0., 1.005, r'$\bf{{CMS}}$', fontsize = 35, transform = ax.transAxes)
        ax.text(0.2, 1.005, r'$\it{{Preliminary}}$', fontsize = 30, transform = ax.transAxes)
        ax.text(0.7, 1.005, r'138 fb$^{-1}$ (13 TeV)', fontsize = 20, transform = ax.transAxes)
        ax.text(0.63, 0.9, r'H$\rightarrow$ ZZ', fontsize = 25, transform = ax.transAxes)
        ax.text(0.55, 0.85, r'm$_{\mathrm{H}}$ = 125.38 GeV', fontsize = 25, transform = ax.transAxes)

        mask = np.zeros_like(theMap)
        mask[np.triu_indices_from(mask, k = 1)] = True
        palette = sns.diverging_palette(240, 10, n=20, as_cmap = True)

        hmap = sns.heatmap(theMap,
                mask = mask,
                vmin=-1.0, vmax=1.0,
        #         xticklabels=ticks,
        #         yticklabels=ticks,
                annot = True,
                fmt = '.2f',
                square = True,
                annot_kws={'size': 12, 'weight': 'bold'},
                cmap = palette,
                cbar_kws={'pad': .005, 'ticks':np.arange(-1.2, 1.2, 0.2)})
        hmap.figure.axes[-1].tick_params(axis = 'y', labelsize =24, direction='in', length = 10) 

        for t in hmap.texts:
            if '-0.00' in t.get_text():
                t.set_text('0.00')

        plt.yticks(rotation=0, fontsize = 20) 
        plt.xticks(fontsize = 20) 

        plt.axhline(y=0, color='k',linewidth=2.5)
        plt.axhline(y=theMap.shape[1], color='k',linewidth=2.5)
        plt.axvline(x=0, color='k',linewidth=2.5)
        plt.axvline(x=theMap.shape[0], color='k',linewidth=2.5)

        plt.savefig('datacardInputs/allYear/corr_'+obsName+'_'+physicalModel+opt.BKG+'.pdf', bbox_inches='tight')


if 'vs' in opt.OBSNAME:
    obsName_tmp = opt.OBSNAME.split(' vs ')
    obsName = obsName_tmp[0]+'_vs_'+obsName_tmp[1]
    OneDOr2DObs=2
    obs_reco2 = obsName_tmp[1]
else:
    obsName = opt.OBSNAME
    obs_reco2 = ''
    OneDOr2DObs=1
print "OneDOr2DObs:  ", OneDOr2DObs
   
DataModelName = 'SM_125'
if (obsName=="mass4l"):
    PhysicalModels = ['v2','v3']
#elif obsName == 'D0m' or obsName == 'Dcp' or obsName == 'D0hp' or obsName == 'Dint' or obsName == 'DL1' or obsName == 'DL1Zg' or obsName == 'costhetaZ1' or obsName == 'costhetaZ2'or obsName == 'costhetastar' or obsName == 'phi' or obsName == 'phistar' or obsName == 'massZ1' or obsName == 'massZ2':
#    PhysicalModels = ['v3','v4']
else:
    PhysicalModels = ['v3']



sys.path.append('./combine_files/')
if 'v2' in PhysicalModels:
    _temp = __import__('inputs_sig_'+obsName, globals(), locals(), ['observableBins'], -1)
    acc = _temp.acc


ObsToStudy = "1D_Observables" if OneDOr2DObs == 1 else "2D_Observables"
print "ObsToStudy:  ", ObsToStudy
with open(opt.inYAMLFile, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
    obs_bins_yml = cfg['Observables'][ObsToStudy][opt.OBSNAME]['bins'] 

act_bins_yml = read_bins(obs_bins_yml)
print "obs_bins_yml  ", obs_bins_yml
print " pairs bins obs_bins_yml  ", act_bins_yml

nBins = len(act_bins_yml)



if obs_reco2 == '':
        nBins = nBins - 1 

print "obsName: ", obsName
print "obs_reco2: ", obs_reco2


print "nBins:  ", nBins




RunCombineCorrelation()
print "now to plot correlation matrix."

PlotCorrelation()

print "correlation matrix for observable ", obsName, " has been produced."


sys.path.remove('./datacardInputs/2018/')
