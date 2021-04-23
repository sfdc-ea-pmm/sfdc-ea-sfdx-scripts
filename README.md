# Shell scripts for  SFDX Einstein Analytics Template Developement
This repo contains the scripts needed to develop Einstein Analytics Demo Templates with SFDX

### Development Flow
[Image]

## Prerequisite
Before trying the steps detailed here, you need the following:
1. A working Salesforce Dev Hub org.
2. Prior experience with Salesforce DX and Salesforce CLI.
3. Basic understanding of Salesforce Einstein Analytics.
4. Setup environment as below.

## Environment Setup
### Salesforce CLI
1. Install Salesforce CLI from https://developer.salesforce.com/tools/sfdxcli. Follow the instructions on that page to download.
2. Open a terminal
    1. Install the Analytics plugin by running the command ` `
    2. Install shane-sfdx-plugins for additional functionality `sfdx plugins:install shane-sfdx-plugins`
3. Authorize a dev hub `sfdx force:auth:web:login -d -a [ALIAS]`
    1. Login to a dev hub and you can close the window
4. Authorize any additional orgs with `sfdx force:auth:web:login -a [ALIAS]`
    1. Login to org and you can close the window
5. Check your authorized orgs by running `sfdx force:org:list`

### Python 3
* Python version 3.6 installed locally. See the installation guides for 
  [OS X](http://docs.python-guide.org/en/latest/starting/install3/osx/), 
  [Windows](http://docs.python-guide.org/en/latest/starting/install3/win/), and
  [Linux](http://docs.python-guide.org/en/latest/starting/install3/linux/).
* Setuptools and Pip installed locally. See the Python install guides above for 
  installation instructions.

On OS X, you can verify your system by running `python3 --version; pip3 --version`.

While not required, it is recommended you have [virtualenv](https://virtualenv.pypa.io/en/latest/) installed locally to avoid package conflicts. Accomplish this by running  `pip3 install virtualenv` on OS X.

Install all dependencies by running: `pip3 install -r requirements.txt`

## Usage
### Develop with Scratch Org
1. Clone this repo
2. Fork (or clone) or create your own source code folder.
3. Set `path` attibute in `sfdx-project.json` if not using `../sfdc-ea-demo-templates/force-app`
4. Set `adminEmail` in `project-scratch-def.json`
5. Run `python3 scripts/initOrg.py -t [TEMPLATE_API_NAME]`, (where TEMPLATE_API_NAME is the template you want to work on) to create a new Scratch Org with assets from repo. (Scratch Orgs are defaulted to **expire in 1 day**, override with argument `./initOrg.py -d 7`)

### Development
1. Do your development in the scratch org or VS Code.
    * Edit dashboards in the org and pull source to local (see step 4ii below)
    * Edit template metadata in VS Code and push source to scratch org and update (see step 4i below)
2. Use the commands 
    * `SFDX: Push Source to Org` (VS Code) or `sfdx force:source:push` (Salesforce CLI) to push changes from local into the Scratch Org. For example changes to template metadata (i.e. template-info.json)
    * `SFDX: Pull Source from Org` (VS Code) or `sfdx force:source:pull` (Salesforce CLI) to pull changes down from Scratch Org to local. For example, dashboard edits.
3. Run `./scripts/updateTemplate.sh` to update template with latest changes
4. Sync code with git

### Deploy template to non scratch org
1. Use `sfdx force:auth:web:login -a [ALIAS]` to add your non scratch org (First time only)
2. Run `python3 scripts/deployTemplate2NonScratchOrg.py -u <TARGET ORG ALIAS> -t <TEMPLATE API NAME>` to specified template into target org or Use the command `SFDX: Deploy Source to Org` if using VS Code
    e.g. `python3 scripts/deployTemplate2NonScratchOrg.py -u targetSDO -t Key_Account_Management` (target folder name of the template, under force-app/main/default/waveTemplates)

### Retreive template from a source org
Use the following to convert an existing app to a template to commit to source control or with the `deployTemplate2NonScratchOrg.py` script this can also be used to migrate assets from one org to another.

#### Preq 
App in source org needs to be converted into a template and packaged first
1. Run `sfdx analytics:app:list -u [SOURCE ORG ALIAS]` to get the list of the apps
2. If the app was created from a template, you'll need to first decouple with `sfdx analytics:app:decouple -u [SOURCE ORG ALIAS] -f [FOLDER ID OF APP] -t [TEMPLATE ID]`
3. All assets (i.e. datasets, lenses, dashboards) should be moved into the same app.
4. Run `sfdx analytics:template:create -u [SOURCE ORG ALIAS] -f [FOLDER ID OF APP]` to create a new template
    * Or run `sfdx analytics:template:update -u [SOURCE ORG ALIAS] -t [TEMPLATE ID TO UPDATE]` to update an existing template
5. Go to Setup --> Manage Packages and create a new package with the Einstein Analytics assets. No need to upload. 

#### Retrieve the source
1. Run `python3 scripts/retrieveTemplate.py -u [SOURCE ORG ALIAS] -p [PACKAGE NAME] -a [APP API NAME containing datasets to include]` e.g `python3 scripts/retrieveTemplate.sh -u shared-sales -p CLA_Demo -a "Customer_Lifecycle_Analytics_Demo"`
2. Once the script completes, the source for the selected packaged template will be available in the sfdx_temp folder. There also a couple manual steps that need to be taken:
    1. Move dataset XMD files into `external_files` from `waveTemplates/dataset_files` if datasets are not created by dataflow
    2. Create datasets schema files, by using Create Dataset UI in Analytics Studio.
        1. Create --> Dataset --> CSV File --> Upload File --> Next --> Make any changes if needed --> Back --> Data Schema File --> Download File
        2. Save file into both `external_files` and `fulldata`
    3. Rename any datasets names that end with a # and update references in dashboard json and template-info.json
    4. Update template-info.json so that the external files are referenced along with the csv, schema and xmd
    5. Fix dot notations in dashboard json where needed
3. Test the template by deploying the new template. Following sections above:
    * Spin up a scratch org i.e. `python3 scripts/initOrg.py -t Key_Account_Management'` or 
    * Deploy into an non-scratch org i.e. `python3 scripts/deployTemplate2NonScratchOrg.py -u targetSDO -t Key_Account_Management` (target folder name of the template, under force-app/main/default/waveTemplates)
