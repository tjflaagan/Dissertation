num=1
ssh admin@10.0.0.1 -f -x "vmstat -c 100000 -w .5 -H >> ptime$num.txt" 
for i in `seq 0 1000`; do (time python3 external_portfwd.py) &>> ptime$num.txt; done
pid=`ssh admin@10.0.0.1 -x "pgrep vmstat"`
ssh admin@10.0.0.1 -x "kill $pid"