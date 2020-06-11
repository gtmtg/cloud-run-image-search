if [[ $# -ne 1 ]]; then
    echo "Usage: ./deploy.sh [subdir]"
    exit 1
fi

branch=`git rev-parse --abbrev-ref HEAD`
project=`gcloud config get-value project 2> /dev/null`
folder=`echo $1 | sed 's:/*$::'`
name=mihir-$folder-$branch
root_path=..

if [[ "$project" != "kayvonf-cloud-run-experiments" ]]; then
    echo "Must be deployed on whitelisted project kayvonf-cloud-run-experiments"
    exit 2
fi

# Copy shared resources in
cp common/* $folder
cp -r $root_path/src/knn $folder

# Submit build from within subdirectory
gcloud config set builds/use_kaniko True
(cd $folder; gcloud builds submit --tag gcr.io/$project/$name)

# Remove shared resources
for file in $(ls common/)
do
   rm $folder/"$file"
done
rm -rf $folder/knn

# Deploy Cloud Run handler
./reset.sh $folder
