cd ../indexer/  # navigate to crawler directory

while getopts f:d:t:c:m:q: flag
do
    case "${flag}" in
        f) filename=${OPTARG};;
        d) directory=${OPTARG};;
        t) testing=${OPTARG};;
        c) resultCount=${OPTARG};;
        m) sampleSize=${OPTARG};;
        q) queryType=${OPTARG};;
    esac
done

python3 indexer.py filename=$filename directory=$directory resultCount=$resultCount testing=$testing sampleSize=$sampleSize queryType=$queryType