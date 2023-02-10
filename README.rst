
=========================================
FiducialXS README Page
=========================================
Instructions to run the xBF team's framework for differential cross-section measurements for CMSSW_10_X releases.
=========================================

Dependencies:

.. image:: https://img.shields.io/static/v1?label=CMSSW%20version&message=10_2_X&color=brightgreen
.. image:: https://img.shields.io/static/v1?label=Combine%20version&message=8_2_0&color=brightgreen

Framework/documentation:

.. image:: https://readthedocs.org/projects/fiducialxs/badge/?version=latest

Detailed documentation regarding the framework can be found in the dedicated `ReadTheDocs <https://fiducialxs.readthedocs.io/en/latest/?badge=latest>`_ page.
This ``README`` file and the official documentation are written in ``.rst`` (ReStructured Text Markup syntax) in order to better explore the options given by ``sphinx`` and ``ReadTheDocs``.
For more details about the Markup syntax, please consult the `ReStructuredText Primer <https://docutils.sourceforge.io/docs/user/rst/quickstart.html>`_.


1. Setup the correct CMSSW and Combine releases
=========================================
These are formed from from the `official Combine framework instructions <https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/>`_.

CC7 release CMSSW_10_2_X - recommended version
Setting up the environment (once): ::

  export SCRAM_ARCH=slc7_amd64_gcc700
  cmsrel CMSSW_10_2_13
  cd CMSSW_10_2_13/src
  cmsenv
  git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
  cd HiggsAnalysis/CombinedLimit

Update to a recommended tag - currently the recommended tag is v8.2.0: see release notes: ::


  cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
  git fetch origin
  git checkout v8.2.0
  scramv1 b clean; scramv1 b # always make a clean build

Depending on where the data/mc is stored, one might need: ::

  voms-proxy-init -voms cms

Final step is to clone the correct verison of the code. At the moment the working version can be found on the ```CMSSW_10_X``` branch, which can be cloned via the following command: ::

  cd $CMSSW_BASE/src/
  git clone -b CMSSW_10_X git@github.com:YujiLee301/Fiducial_XS.git
  cd Fiducial_XS
  
  source setup.sh # mandatory to load necessary library
  # or run following manually:
  # export PYTHON27PATH=$PYTHON27PATH:python
  # export PYTHON27PATH=$PYTHON27PATH:Inputs

1.1 importing datacards
=========================================
Currently Yuji has added datacard for pT4l, and ones can copy from the path: ::

  cp -r /afs/cern.ch/user/y/yujil/public/datacardInputs .

2. Running the measurement
=========================================

2.1 Using the ``RunEverything.py`` script:
-----------------------------------------

Now, all steps can be run using script ``RunEverything.py``. The available options are: ::


  usage: RunEverything.py [-h] [-s {1,2,3,4,5}] [-c CHANNELS [CHANNELS ...]]
                        [-p NTUPLEDIR] [-m HIGGSMASS] [-r {0,1}]

  Input arguments

  optional arguments:
    -h, --help            show this help message and exit
    -s {1,2,3,4,5}        Which step to run
    -c CHANNELS [CHANNELS ...]
                          list of channels
    -p NTUPLEDIR          Path of ntuples
    -m HIGGSMASS          Higgs mass
    -r {0,1}              if 1 then it will run the commands else it will just
                          print the commands
    -i                    choose the observable list

Commands to run: ::


  python RunEverything.py -r 1 -s 1 # step-1: Compute efficiencies
  python RunEverything.py -r 1 -s 2 # step-2: collectInputs
  python RunEverything.py -r 1 -s 3 # step-3: interpolation for powheg sample
  python RunEverything.py -r 1 -s 4 # step-4: Run uncertainty step
  python RunEverything.py -r 1 -s 5 # step-5: interpolation for the NNLOPS sample using powheg sample
  python RunEverything.py -r 1 -s 6 # step-6: Run background template maker
  python RunEverything.py -r 1 -s 7 # step-7: Final measurement and plotter
  
Note that if the datacard directory is downloaded, you can start from step-6 to create template: ::


  python RunEverything.py -r 1 -s 6 -i "Inputs/observables_yuji.yml"
  python RunEverything.py -r 1 -s 7 -i "Inputs/observables_yuji.yml"


General
^^^^^^^^^^^^^^^^^^

1. Add the `choices` for argparser whereever its possible. So, that code won't run if we provide wrong arguments.

Hardcoded Informations
^^^^^^^^^^^^^^^^^^

1. obsList YAML file should follow the following format:

  ```YAML
  Observables:
    1D_Observables:
      mass4l:
        - bins: "|105.0|140.0|"
    2D_Observables:
      mass4l:
        - bins: "|105.0|140.0|"
  ```

  In this YAML file the two names `Observables`, `1D_Observables` and `2D_Observables` should remain same, else the code will give error.
