#!/bin/bash

#configuring postgresql network--------------------------------------------
echo "Teste? (s/n) "; read sim
sim="${sim:=s}"
echo $sim
if [ "$sim" == "s" ]; then
	echo "SIM SIM"
fi
#----------------installing and configuring packages--------------------------------------------

exit