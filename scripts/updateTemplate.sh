#!/bin/zsh
##################################################################################################################
# Automate commands to update template with dashboard changes and pull source from org to local
# Created by: Terrence Tse, ttse@salesforce.com
# Last Updated: Feb 19, 2020
##################################################################################################################

# constants
## API name of template
TEMPLATE_API_NAME="Einstein_Analytics_Starter_Pack"

## echo colors
ERROR='\033[0;31m' # Red
WARN='\033[1;33m' # Yellow
MSG='\033[1;36m' # Lighy Cyan
NC='\033[0m' # No Color

# Argument Usage
print_usage() {
    echo
    echo "Usage:"
    echo "  deployTemplateNonScratch.sh -u <TARGET ORG ALIAS> -t <TEMPLATE API NAME>"
    echo
    echo "Arguments:"
    echo "    -u    alias of target org to deploy to"
    echo "    -t    template api name to deploy, should be same as folder name under waveTemplates/"
    echo "e.g. `./scripts/updateTemplate.sh -u targetSDO -t Key_Account_Management`"
    echo
}

while getopts 'hu:t:' flag; do
  case "${flag}" in
    u)  TARGET_ORG_ALIAS="${OPTARG}";;
    t)  TEMPLATE_API_NAME="${OPTARG}";;
    h)  print_usage
        exit 0 ;;
    \?) print_usage
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

# print args
echo "TEMPLATE_API_NAME=${WARN}$TEMPLATE_API_NAME${NC}"

# get template ID
TEMPLATE_ID="$(sfdx analytics:template:list | grep $TEMPLATE_API_NAME | cut -d ' ' -f3)"

# Update Template
echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Updating template ID: $TEMPLATE_ID...${NC}"
sfdx analytics:template:update  -u $TARGET_ORG_ALIAS -t $TEMPLATE_ID

# Pull latest source to local
echo "${MSG}$(date "+%Y-%m-%d %H:%M:%S")|[INFO] Pulling latest source to local...${NC}"
sfdx force:source:pull -u $TARGET_ORG_ALIAS