# Copy shared resources in
cp common/* $1
cp -r ../src/knn $1

# Run server from within subdirectory
(cd $1; LRU_CACHE_CAPACITY=1 uvicorn --host "0.0.0.0" --port $2 --workers 1 handler:mapper)

# Remove shared resources
for file in $(ls common/)
do
   rm $1/"$file"
done
rm -rf $1/knn
