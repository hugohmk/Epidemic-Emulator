if [ $# -ne 3 ]
then
  recovery=1.0
  endogenous=1.1
  exogenous=0.1
else
  recovery=$1
  endogenous=$2
  exogenous=$3
fi

echo "Using r=$recovery, e=$endogenous, x=$exogenous"

node=1
while [ $node -lt 10 ]; do
  echo "Launching node $node"
  python /home/gdcs/Epidemic-Emulator/main.py -id $node -r $recovery -e $endogenous -x $exogenous &
  node=$((node+1))
done

echo "Launching node 0"
python /home/gdcs/Epidemic-Emulator/main.py -id 0 -i 20 -r $recovery -e $endogenous -x $exogenous