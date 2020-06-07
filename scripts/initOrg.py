##################################################################################################################
# Script to spin up a Scratch Org and initialize the org with data for Template being developed
# Created by: Terrence Tse, ttse@salesforce.com
# Last Updated: Jun 4, 2020
##################################################################################################################

import json,sys,csv,os,re,argparse,logging

from datetime import datetime

# constants
## timestamp
TIMESTAMP=datetime.now().strftime("%Y%m%d%H%M%S")

def run(args):
    # print args
    logging.info('TIMESTAMP=%s' % TIMESTAMP)
    logging.info(args)

    logging.info("Creating sfdx_temp folder...")
    if not os.path.exists('sfdx_temp'):
        os.mkdir("sfdx_temp")

    # create scratch org
    logging.info(("Creating Scratch Org with Duration: %s..." % args.duration))
    os.system( ("sfdx force:org:create -f config/project-scratch-def.json -s -d %s -w 60" % args.duration) )

    # push source
    logging.info("Pushing source...")
    #stream = os.popen("sfdx force:source:push -f")
    # sfdx_temp directory for working files
    logging.info("Deploying static resources...")
    os.system( ("sfdx force:source:deploy -p %s/staticresources" % (args.path) ))
    logging.info("Deploying wave templates...")
    os.system( ("sfdx force:source:deploy -p %s/waveTemplates/%s" % (args.path, args.template) ))
    #output = stream.read()

    if args.sample==True:
        # load demo/testing Data
        logging.info("Loading Demo/Testing Data...")

        #prep unique Username in User csv
        os.system( ("sed \"s/{TIMESTAMP}/%s/g\" data/core/User.csv > sfdx_temp/User_Load.csv" % TIMESTAMP) )

        ## load csvs into core objects
        os.system("sfdx force:data:bulk:upsert -s UserRole -f data/core/UserRole.csv -i Name -w 2")
        os.system("sfdx force:data:bulk:upsert -s User -f sfdx_temp/User_Load.csv -i External_Id__c -w 2")
        os.system("sfdx force:data:bulk:upsert -s Account -f data/core/Account.csv -i External_Id__c -w 5")
        os.system("sfdx force:data:bulk:upsert -s Opportunity -f data/core/Opportunity.csv -i External_Id__c -w 5")

        os.system("sfdx force:data:record:create -s Task -v \"Subject='Sample Task'\"")
        os.system("sfdx force:data:record:create -s Event -v \"Subject='Sample Call' DurationInMinutes='1' ActivityDateTime='2019-01-01'\"")

        os.system("sfdx force:data:record:create -s Case -v \"Subject='Sample Case'\"")

        os.system("sfdx force:data:record:create -s Campaign -v \"Name='Sample Campaign'\"")

        #sfdx force:data:record:create -s CampaignMember -v "LastName='Sample CampaignMember'"

        os.system("sfdx force:data:record:create -s Lead -v \"LastName='Sample Lead' Company='Sample Company'\"")

        os.system("sfdx force:data:record:create -s Contact -v \"LastName='Sample Contact'\"") 

    if args.template: 
        # get template ID
        stream = os.popen("sfdx analytics:template:list")
        output = stream.read().splitlines()
        header = re.split(r'\s{2,}',output[1])

        for row in output:
            if not (row.startswith("===") or row.startswith("───")):
                rowArr = re.split(r'\s{2,}',row)
                if rowArr[header.index("NAME")] == args.template:
                    template_id = rowArr[header.index("TEMPLATEID")]

        # create MASTER app
        logging.info("Creating App with Template ID : %s" % template_id)
        logging.info("Please be patient, it may take up to 15 mins")

        os.system( ("sfdx analytics:app:create -t %s -w 15" % template_id) )

        # link folder to template
        stream = os.popen("sfdx analytics:app:list")
        output = stream.read().splitlines()
        header = re.split(r'\s{2,}',output[1])
        for row in output:
            if not (row.startswith("===") or row.startswith("───")):
                rowArr = re.split(r'\s{2,}',row)
                if rowArr[header.index("NAME")] == args.template:
                    folder_id = rowArr[header.index("FOLDERID")]

        logging.info(("Linking App with Folder ID: %s with Template ID: %s..." % (folder_id, template_id) ) )

        os.system( ("sfdx analytics:template:update -t %s -f %s" % (template_id, folder_id)) )
        
    #os.system( ("sfdx force:user:password:generate") )
    os.system( ("sfdx force:org:open -p /analytics/wave/wave.apexp#home") )
    logging.info("Scratch Org is ready." )

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %I:%M:%S',level=logging.DEBUG)
    
    # Create the parser
    my_parser = argparse.ArgumentParser(prog='initOrg',description='Initialize a Scratch Org for Einstein Analytics Template development')

    # Add the arguments
    my_parser.add_argument('-t','--template',type=str,help='specify template (api name) to deploy, should be same as folder name under waveTemplates/.')
    my_parser.add_argument('-s','--sample',default=False,action='store_true',help='include sample data in scratch org')
    my_parser.add_argument('-d','--duration',type=int,default=1,choices=range(1, 30),help='set scratch org duration')
    my_parser.add_argument('-p','--path',type=str,default='../sfdc-ea-demo-templates/force-app/main/default',help='overide source deploy path')

    run(my_parser.parse_args())