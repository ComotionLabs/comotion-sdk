

## partition error

load_id=$(comotion -opoc2 dash create-load -s0 -p "hello2" -p "hello3" hello) 
comotion -opoc2 dash upload-file-to-load -l$load_id ./large_3gb.parquet
comotion dash commit-load -l$load_id -c "count(*)" "10000000"
comotion dash get-load-info -l$load_id
load_status=$(comotion dash get-load-info -l$load_id)
load_messages=$(comotion dash get-load-info -l$load_id 2>&1 > /dev/null)
echo $load_messages


## no errors

load_id=$(comotion -opoc2 dash create-load -s0 -p "booleans" hello) 
comotion -opoc2 dash upload-file-to-load -l$load_id ./large_3gb.parquet
comotion dash commit-load -l$load_id -c "count(*)" "10000000"
comotion dash get-load-info -l$load_id
load_status=$(comotion dash get-load-info -l$load_id)
load_messages=$(comotion dash get-load-info -l$load_id 2>&1 > /dev/null)
echo $load_messages