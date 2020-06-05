#!/bin/zsh
##################################################################################################################
# Script to create source from template
# Created by: Terrence Tse, ttse@salesforce.com
# Last Updated: Apr 21, 2020
##################################################################################################################

# constants
TIMESTAMP=$(date "+%Y%m%d%H%M%S") # timestamp for logging

## echo colors
ERROR='\033[0;31m' # Red
WARN='\033[1;33m' # Yellow
MSG='\033[1;36m' # Light Cyan
NC='\033[0m' # No Color

#variables
SOURCE_ORG_ALIAS='' # Alias of authenticated Source Org to pull template from
PACKAGE_NAME='' # Name of package to retrieve
API_VERSION='48.0'

# Argument Usage
print_usage() {
  echo
    echo "Usage:"
    echo "  retrieveTemplate.sh -u <SOURCE ORG ALIAS> -p <PACKAGE NAME> [ -a <APP API NAME> ]"
    
    echo "Arguments:"
    echo "    -u    alias of source org to retrieve from"
    echo "    -p    name of package containing templates assets to retrieve"
    echo "    -a    [optional] name of app containing datasets to extract "
    echo "e.g. scripts/retrieveTemplate.sh -u shared-sales -p CLA_Demo -a \"Customer_Lifecycle_Analytics_Demo\""
    echo
}

while getopts 'a::p:u:' flag; do
  case "${flag}" in
    a) APP_API_NAME="${OPTARG}";;
    p) PACKAGE_NAME="${OPTARG}";;
    u) SOURCE_ORG_ALIAS="${OPTARG}";;
    *) print_usage
       exit 1 ;;
  esac
done

if ((OPTIND == 1))
then
    echo "${WARN}No arguments specified${NC}"
    print_usage
    exit 1
fi

shift $((OPTIND-1))

TEMP_FOLDER=sfdx_temp/${PACKAGE_NAME}_$TIMESTAMP
mkdir -p $TEMP_FOLDER

echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Retrieving package, $PACKAGE_NAME from $SOURCE_ORG_ALIAS and unzipped to $TEMP_FOLDER.${NC}"
sfdx force:mdapi:retrieve -u $SOURCE_ORG_ALIAS -r $TEMP_FOLDER -p $PACKAGE_NAME 
 
 # uncompress retrieved zip
unzip -o $TEMP_FOLDER/unpackaged.zip -d $TEMP_FOLDER

echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Package retrieved and uncompressed.${NC}"

# download datasets if specified
if [ -z "$APP_API_NAME" ]
then
  echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] No datasets specified.${NC}"
  exit 0
else
  echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Extracting datasets from $APP_API_NAME...${NC}"
  
  mkdir -p $TEMP_FOLDER/external_files
  mkdir -p $TEMP_FOLDER/data/analytics/$APP_API_NAME

  arr=(${(f)"$(sfdx force:data:soql:query  -u $SOURCE_ORG_ALIAS -q "SELECT DeveloperName FROM Edgemart WHERE InsightsApplication.DeveloperName='$APP_API_NAME'")"})

  for s in "${arr[@]}"; do
    echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Downloading dataset: $s${NC}"
    sfdx shane:analytics:dataset:download -u $SOURCE_ORG_ALIAS -t $TEMP_FOLDER/data/analytics/$APP_API_NAME -b 10000 -n $s
  done

  echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Datasets downloaded to $TEMP_FOLDER/external_files${NC}"

  # sample data for template
  for csv_file in $TEMP_FOLDER/data/analytics/$APP_API_NAME/*.csv; do
      head -n 5000 $csv_file > $TEMP_FOLDER/external_files/$csv_file:t
  done
fi
