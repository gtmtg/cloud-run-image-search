name=mihir-benchmark-`basename ~+`
folder=mapper
region=us-central1
root_path=../..
port=${1:-1234}

# Copy shared resources in
cp -r $root_path/src/knn $folder

# Run handler from within subdirectory
(cd $folder && wget -i resources.txt && uvicorn --host "0.0.0.0" --port $port --workers 1 handler:mapper)

# Remove shared resources
rm -rf $folder/knn
