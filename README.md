# Azure Account Setup - Terraform

Python script to setup the remote backend in Azure that can then be consumed by Terraform.

__**Requirements**__

The requirements for the script itself are all stored in requirements.txt, which can be installed using the below command.

```bash
pip install -r requirements.txt
```

A pre-requisite to running the script is setting some environmental variables, they are as follows.\

```bash
export AZURE_TENANT_ID=$YourTenantID
export AZURE_CLIENT_ID=$YourClientID
```

You'll also need to create a Service Principal.

```bash
az ad sp create-for-rbac --name $YourServicePrincipalName
```

Once the Service Principal has been created you will need to export the following

```bash
export AZURE_CLIENT_ID=$YourClientID
export AZURE_CLIENT_SECRET=$YourClientSecret
```

You should then be able to run the python script

```bash
python accountsetup.py
```

The script takes several flags, which can all be found by running the script with -h
