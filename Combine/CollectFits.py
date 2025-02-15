# Script to collect fit outputs

import os, sys
import re
from optparse import OptionParser
import glob
import json

print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG COLLECT FITS RUN II ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "

def get_options():
  parser = OptionParser()
  parser.add_option('--inputJson', dest='inputJson', default='inputs.json', help="Input json file to define fits")
  parser.add_option('--mode', dest='mode', default='mu_inclusive', help="Type of fit")
  parser.add_option('--ext', dest='ext', default='', help="If txt datacard has extension")
  parser.add_option('--extIn', default=None, type=str, help="if extension in, overwrite")
  parser.add_option('--doObserved', dest='doObserved', action="store_true", default=False, help="Fit to data")
  return parser.parse_args()
(opt,args) = get_options()

def leave():
  print " ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ HGG COLLECT FITS RUN II (END) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
  sys.exit(1)

def run(cmd):
  #print "%s\n"%cmd
  os.system(cmd)


# Read json file
with open( opt.inputJson ) as jsonfile: inputs = json.load(jsonfile)[opt.mode]
# Extract info
pois = inputs['pois'].split(",")
fits = inputs['fits'].split("+")

# Create plots directory in mode
ext = '%s_%s' % (opt.ext, opt.mode)
if opt.extIn is not None:
  ext = opt.extIn
my_dir = 'runFits_%s' % ext
if not os.path.isdir("%s/Plots"%(my_dir)): os.system("mkdir %s/Plots"%(my_dir))
# Loop over fits: hadd and then plot
for fidx in range(len(fits)):
  _fit = fits[fidx]
  if _fit.split(":")[2] == "all": _fitpois = pois
  else: _fitpois = _fit.split(":")[2].split(",")
  _name = "%s_%s"%(_fit.split(":")[0],_fit.split(":")[1])
  if opt.doObserved: 
    _name += "_obs"
    mainlabel = "Observed"
  else:
    mainlabel = "Expected"
  # add this to distinguish different fits with same POI
  _name += "_"+opt.ext

  if( _fit.split(":")[0] == "bestfit" ):
    for poi in _fitpois:
      mvcmd = "cd %s; mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s_%s.root; cd .."%(my_dir,_name,poi,_name,poi)
      print " --> Storing best fit: %s/%s_%s.root"%(my_dir,_name,poi)
      run(mvcmd)

  elif( _fit.split(":")[0] == "fixed" ):
    for poi in _fitpois:
      mvcmd = "cd %s; mv higgsCombine_%s_%s.MultiDimFit.mH125.root %s.root; cd .."%(my_dir,_name,poi,_name)
      print " --> Storing fixed point: %s/%s.root"%(my_dir)
      run(mvcmd)

  elif( _fit.split(":")[0] == "profile1D")|( _fit.split(":")[0] == "scan1D" ):
    for poi in _fitpois:
      if poi in ["r_ggH","r_VBF","r_top","r_VH"]:
        translate_json = "pois_mu.json" 
      elif poi=='CMS_zz4l_fai1':
        if 'ALT_0M' in opt.ext: translate_json = "pois_fa3.json"
        if 'ALT_0PH' in opt.ext: translate_json = "pois_fa2.json"
        if 'ALT_L1' in opt.ext: translate_json = "pois_flambda1.json"
        if 'ALT_L1Zg' in opt.ext: translate_json = "pois_flambda1zgamma.json"
      else:
        print "Warning: unknown poi. Use r as default"
        translate_json = "pois_mu.json"
      haddcmd = "cd %s; hadd -f %s_%s.root higgsCombine_%s_%s.POINTS.*.*.root; cd .."%(my_dir,_name,poi,_name,poi)
      print '-------------------------------------------------------------------------------------------------'
      print '-------------------------------------------------------------------------------------------------'
      print '======== ' + '%s/%s_%s.root' % (os.getcwd(),_name, poi)
      print '-------------------------------------------------------------------------------------------------'
      print '-------------------------------------------------------------------------------------------------'
      print '-------------------------------------------------------------------------------------------------'
      run(haddcmd)
      plotcmd = "cd %s; plot1DScan.py %s_%s.root --y-cut 30 --y-max 30 -o Plots/%s_%s%s --POI %s --main-label %s --translate %s/src/flashggFinalFit/Plots/%s; cd .."%(my_dir,_name,poi,_name,poi,opt.ext,poi,mainlabel,os.environ['CMSSW_BASE'],translate_json)
      print "plotcmd = ",plotcmd
      run(plotcmd)

  elif( _fit.split(":")[0] == "scan2D")|( _fit.split(":")[0] == "profile2D" ):
    _poisStr = "%s_vs_%s"%(_fitpois[0],_fitpois[1])
    haddcmd = "cd %s; hadd -f %s_%s.root higgsCombine_%s_%s.POINTS.*.*.root; cd .."%(my_dir,_name,_poisStr,_name,_poisStr)
    run(haddcmd)
    
