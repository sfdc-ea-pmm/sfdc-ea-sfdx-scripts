##################################################################################################################
# Script to create source from template
# Created by: Terrence Tse, ttse@salesforce.com
# Last Updated: Jun 4, 2020
##################################################################################################################

import json,sys,csv,os,re,argparse,logging,requests,pandas,random
from zipfile import ZipFile

from datetime import datetime

# constants
TIMESTAMP=datetime.now().strftime("%Y%m%d%H%M%S") #timestamp

def createCSVSchema(df):
    df.dtypes

def run(args):
    # print args
    logging.info('TIMESTAMP=%s' % TIMESTAMP)
    logging.info(args)

    logging.info("Creating sfdx_temp folder...")
    temp_folder = ( "sfdx_temp/%s_%s" % (args.package,TIMESTAMP) )
    os.makedirs(temp_folder, exist_ok=True)
    
    logging.info("Retrieving package, %s from %s and unzipped to %s." % (args.package, args.targetuseralias, temp_folder))
    os.system( ("sfdx force:mdapi:retrieve -u %s -r %s -p %s" % (args.targetuseralias, temp_folder, args.package)) )

    with ZipFile(('%s/unpackaged.zip' % temp_folder), 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(temp_folder)

    logging.info("Package retrieved and uncompressed.")

    if args.app:
        logging.info("Extracting datasets from %s" % args.app)

        fulldata_path = ("%s/fulldata" % temp_folder)
        externalfiles_path = ( "%s/%s/waveTemplates/%s/external_files" % (temp_folder,args.package, args.app) )

        os.makedirs(fulldata_path, exist_ok=True)
        os.makedirs(externalfiles_path, exist_ok=True)

         # get template ID
        stream = os.popen( ("sfdx force:data:soql:query -u %s -q \"SELECT DeveloperName FROM Edgemart WHERE InsightsApplication.DeveloperName='%s'\"" % (args.targetuseralias, args.app) ))
        output = stream.read().splitlines()
        logging.debug(output)

        for row in output:
            if not (row.startswith("DEVELOPERNAME") or row.startswith("───") or row.startswith("Total number of records")):
                logging.info("Downloading dataset: %s" % row)
                os.system( ("sfdx shane:analytics:dataset:download -u %s -t %s -b 10000 -n %s" % (args.targetuseralias, fulldata_path, row)) )

                fullcsv = '%s/%s.csv' % (fulldata_path, row)
                samplecsv = '%s/%s.csv' % (externalfiles_path, row)

                # Count the lines or use an upper bound
                num_lines = sum(1 for l in open(fullcsv))
                logging.debug('CSV Numlines: %d' % num_lines)
                
                if num_lines > 10000:
                    # Sample size - in this case ~10%
                    size = int(10000)
                    logging.debug('Sample Size: %d' % size)

                    # The row indices to skip - make sure 0 is not included to keep the header!
                    skip_idx = random.sample(range(1, num_lines), num_lines - size)

                    # Read the data
                    df = pandas.read_csv(fullcsv, skiprows=skip_idx)
                    df.to_csv(samplecsv,index=False,quoting=csv.QUOTE_NONNUMERIC)
                else:
                    os.system( ("cp %s %s" % (fullcsv, samplecsv)) )
       
        logging.info("Full datasets downloaded to %s with Sample datasets in %s" % (fulldata_path, externalfiles_path) )

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S',level=logging.DEBUG)
    
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='retrieveTemplate',description='Retrieve app assets as template from org')

    # Add the arguments
    my_parser.add_argument('-u','--targetuseralias',required=True,type=str,help='username or alias for the target org; overrides default target org')
    my_parser.add_argument('-p','--package',required=True,type=str,help='name of package containing templates assets to retrieve')
    my_parser.add_argument('-a','--app',type=str,help='app containing datasets to extract')

    run(my_parser.parse_args())