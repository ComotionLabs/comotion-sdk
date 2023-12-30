

## partition error
export COMOTION_ORGNAME=poc2
load_id=$(comotion  dash create-load -s0 -p "hello2" -p "hello3" hello) 
comotion - dash upload-file -l$load_id ./large_3gb.parquet
comotion dash commit-load -l$load_id -c "count(*)" "10000000"
comotion dash get-load-info -l$load_id
load_status=$(comotion dash get-load-info -l$load_id)
load_messages=$(comotion dash get-load-info -l$load_id 2>&1 > /dev/null)
echo $load_status


## no errors
export COMOTION_ORGNAME=poc2
load_id=$(comotion  dash create-load -s0 -p "booleans" hello) 
comotion  dash upload-file -l$load_id ./large_3gb.parquet
comotion dash commit-load -l$load_id -c "count(*)" "10000000"
comotion dash get-load-info -l$load_id
load_status=$(comotion dash get-load-info -l$load_id)
load_messages=$(comotion dash get-load-info -l$load_id 2>&1 > /dev/null)
echo $load_status



## no with file_key
export COMOTION_ORGNAME=poc2
load_id=$(comotion  dash create-load -s0 -p "booleans" hello) 
comotion dash upload-file -khello -l$load_id ./large_3gb.parquet
comotion dash upload-file -khello -l$load_id ./large_3gb.parquet
comotion dash commit-load -l$load_id -c "count(*)" "10000000"
comotion dash get-load-info -l$load_id
