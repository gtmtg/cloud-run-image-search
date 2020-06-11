if [[ $# -ne 1 && $# -ne 2 ]]; then
    echo "Usage: ./local.sh [subdir] [port (optional, default 1234)]"
    exit 1
fi

folder=`echo $1 | sed 's:/*$::'`
port=${2:-1234}

# Copy shared resources in
cp common/* $folder
cp -r ../src/knn $folder

# Run server from within subdirectory
(cd $folder; LRU_CACHE_CAPACITY=1 uvicorn --host "0.0.0.0" --port $port --workers 1 handler:mapper)

# Remove shared resources
for file in $(ls common/)
do
   rm $folder/"$file"
done
rm -rf $folder/knn
