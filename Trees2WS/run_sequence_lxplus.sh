#!/bin/bash

YEAR=-753
STEP=0
DR=
I=

usage(){
    echo "The script runs background scripts:"
    echo "options:"
    
    echo "-h|--help) "
    echo "-y|--year): can be the yearId or all"
    echo "-s|--step) "
    echo "-d|--dryRun) "
    echo "-i|--interactive) "
}
# options may be followed by one colon to indicate they have a required argument
if ! options=$(getopt -u -o s:y:dih -l help,step:,year:,dryRun,interactive -- "$@")
then
# something went wrong, getopt will put out an error message for us
exit 1
fi
set -- $options
while [ $# -gt 0 ]
do
case $1 in
-h|--help) usage; exit 0;;
-y|--year) YEAR=$2; shift ;;
-s|--step) STEP=$2; shift ;;
-d|--dryRun) DR=1;;
-i|--interactive) I=1;;
(--) shift; break;;
(-*) usage; echo "$0: error - unrecognized option $1" 1>&2; usage >> /dev/stderr; exit 1;;
(*) break;;
esac
shift
done

#fggDir="/cmshome/dimarcoe/vbfac/flashgg/CMSSW_10_6_29/src/"
fggDir="/afs/cern.ch/work/f/fcouderc/public/hgg/flashgg/CMSSW_10_6_29/src/"
store_dir="/eos/cms/store/group/dpg_ecal/comm_ecal/localreco/achgg/HiggsCouplings/Trees_2023_07_10_ACCats_VBF_VHHad"


DROPT=""
if [[ $DR ]]; then
    DROPT=" --printOnly "
fi
echo $DROPT

QUEUE="--batch local"
if [[ $I ]]; then
    QUEUE=" --batch local "
else
    QUEUE=" --batch condor --queue microcentury "
    QUEUE=" --batch condor --queue longlunch "
#    QUEUE=" --batch Rome --queue cmsan "
fi
echo $QUEUE

years=("2016preVFP" "2016postVFP" "2017" "2018")
mc_dirs=("TreesV1_signal_IA_UL16preVFP" "TreesV1_signal_IA_UL16postVFP" "_signal_IA_UL17" "TreesV1_signal_IA_UL18")
mkdir -p ${store_dir}/ws/signal/ 
mkdir -p ${store_dir}/ws/data/ 

for idx_y in ${!years[@]}
do
    year=${years[$idx_y]}
    mc_dir=${mc_dirs[$idx_y]}
    json_partial=$fggDir/flashgg/Systematics/test/runAnomCouplings/${mc_dir}/simple_task_manager.json
    OPT="--partial_json ${json_partial}"
    echo $OPT
    if [[ $year == $YEAR ]] || [[ $YEAR == "all" ]]; then
	if [[ $STEP == "t2ws-mc" ]]; then
	    for proc in `ls ${store_dir}/${mc_dir}`; do
		python RunWSScripts.py --inputConfig config.py --inputDir ${store_dir}/${mc_dir}/${proc} --mode trees2ws --modeOpts "${OPT} --doSystematics" --year ${year} --ext GGH_${year}_${proc} ${QUEUE} ${DROPT}
	    done
	elif [[ $STEP == "t2ws-data" ]]; then
	    python RunWSScripts.py --inputConfig config.py --inputDir ${store_dir}/trees/merged/data_${year} --mode trees2ws_data --year ${year} --ext ${year} ${QUEUE} ${DROPT}    
	elif [[ $STEP == "hadd-mc" ]]; then
	    python RunWSScripts.py --inputDir ${store_dir}/trees/merged/signal_${year} --mode haddMC --year ${year} --ext ${year} --flashggPath ${fggDir} ${QUEUE} ${DROPT} --outputWSDir ${store_dir}/ws/signal/
 	elif [[ $STEP == "hadd-data" ]]; then
	    python RunWSScripts.py --inputDir ${store_dir}/trees/merged/data_${year} --mode haddData --year ${year} --ext ${year} --flashggPath ${fggDir} ${QUEUE} ${DROPT} --outputWSDir ${store_dir}/ws/data/
	else
	    echo "Step $STEP is not one among mc, data. Exiting."
	fi
    fi
done


if [[ $STEP == "hadd-data-combine" ]]; then
    ref_dir=`pwd`
    cd $fggDir;
    cmsenv
    cd ${store_dir}/ws/data/
    hadd_workspaces allData_combined.root allData_201*.root
    cd $ref_dir
fi


if [[ $STEP == "rename" ]]; then
    python WSRenamer.py --inputDir ${store_dir}/ws/signal/${year}
fi
