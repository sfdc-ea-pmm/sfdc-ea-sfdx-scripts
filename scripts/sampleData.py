##################################################################################################################
# Create sampled csv
# Created by: Terrence Tse, ttse@salesforce.com
# Last Updated: Jul 2, 2020
##################################################################################################################

import json,sys,csv,os,re,argparse,logging,pandas,random

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
    temp_folder = ( "sfdx_temp/sample_data")
    os.makedirs(temp_folder, exist_ok=True)
    
    logging.info("Sampling %d rows from csv file: %s" % (args.rows, args.input))
   
    fulldata_path = ("%s/fulldata" % temp_folder)
    sampledata_path = ( "%s/sampledata" % (temp_folder) )

    os.makedirs(fulldata_path, exist_ok=True)
    os.makedirs(sampledata_path, exist_ok=True)

    os.system( ("cp %s %s/" % (args.input, fulldata_path)) )

    fullcsv = '%s/%s' % (fulldata_path, os.path.basename(args.input))
    samplecsv = '%s/%s' % (sampledata_path, os.path.basename(args.input))

    # Count the lines or use an upper bound
    num_lines = sum(1 for l in open(fullcsv))
    logging.debug('CSV Numlines: %d' % num_lines)
    
    if num_lines > args.rows:
        # Sample size - in this case ~10%
        size = int(args.rows)
        logging.debug('Sample Size: %d' % size)

        # The row indices to skip - make sure 0 is not included to keep the header!
        skip_idx = random.sample(range(1, num_lines), num_lines - size)

        # Read the data
        df = pandas.read_csv(fullcsv, skiprows=skip_idx)
        df.to_csv(samplecsv,index=False,quoting=csv.QUOTE_NONNUMERIC)
    else:
        os.system( ("cp %s %s" % (fullcsv, samplecsv)) )
    
    logging.info("Full datasets are in %s with Sample datasets in %s" % (fulldata_path, sampledata_path) )

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S',level=logging.DEBUG)
    
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='retrieveTemplate',description='Retrieve app assets as template from org')

    # Add the arguments
    my_parser.add_argument('-i','--input',required=True,type=str,help='csv file to sample')
    my_parser.add_argument('-r','--rows',default=10000,type=int,help='number of rows to output in sample')

    run(my_parser.parse_args())