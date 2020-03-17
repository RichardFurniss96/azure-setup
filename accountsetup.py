#!/usr/bin/python
import argparse
import os
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    StorageAccountUpdateParameters,
    Sku,
    SkuName,
    Kind
)
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient
)
import time

class SetupAccount:

    def __init__(self):
        self.args = self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="bootstrap azure account for terraform backend")

        # Mutually exclusive flags
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-v", "--verbose", action="store_true")
        group.add_argument("-q", "--quiet", action="store_true")

        # Arguements for Azure
        flags = parser.add_argument_group('required flags')
        flags.add_argument("-l", "--location", default="westeurope", help="location for azure resource group")
        flags.add_argument("-rg", "--resource_group", help="name for azure resource group")
        flags.add_argument("-sa", "--storage_account", help="name for azure storage account")
        flags.add_argument("-cn", "--container_name", help="name for azure storage container")

        return parser.parse_args()

    def subscription_id(self):
        subscription_id = os.environ.get(
        'AZURE_SUBSCRIPTION_ID',
        '11111111-1111-1111-1111-111111111111') # your Azure Subscription Id

        return subscription_id

    def credentials(self):
        # Sets credentials list from OS environmental variables
        credentials = ServicePrincipalCredentials(
        client_id=os.environ['AZURE_CLIENT_ID'],
        secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant=os.environ['AZURE_TENANT_ID']
        )
        
        return credentials

    def resource_group(self):
        client = ResourceManagementClient(self.credentials(), self.subscription_id())
        resource_group_params = {'location':self.args.location}

        # Creates AZ resource group with name from arguements and location from arguements
        client.resource_groups.create_or_update(self.args.resource_group, resource_group_params)

        print("Creating resource group: " + self.args.resource_group)

    def storage_account(self):
        # Creates storage account using arguements from above
        storage_client = StorageManagementClient(self.credentials(), self.subscription_id())
        storage_async_operation = storage_client.storage_accounts.create(
            self.args.resource_group,
            self.args.storage_account,
            StorageAccountCreateParameters(
                sku=Sku(name=SkuName.standard_ragrs),
                kind=Kind.storage,
                location=self.args.location
            )
        )
        storage_account = storage_async_operation.result()

        print("Creating storage account: " + self.args.storage_account)
        return storage_account

    def connect_str(self):
        storage_client = StorageManagementClient(self.credentials(), self.subscription_id())
        storage_keys = storage_client.storage_accounts.list_keys(self.args.resource_group, self.args.storage_account)
        storage_keys = {v.key_name: v.value for v in storage_keys.keys}
        connect_str = "DefaultEndpointsProtocol=https;AccountName=" + self.args.resource_group + ";AccountKey=" + storage_keys['key1'] + ";EndpointSuffix=core.windows.net"
        return connect_str

    def storage_container(self):
        blob_service_client = BlobServiceClient.from_connection_string(self.connect_str())
        container_client = blob_service_client.create_container(self.args.container_name)
        return container_client

    def setup_backend(self):
        fin = open("terraform/variables.tf", "rt")
        data = fin.read()
        data = data.replace('rn', str(self.args.resource_group).strip('()'))
        data = data.replace('cn', str(self.args.container_name).strip('()'))
        data = data.replace('sn', str(self.args.storage_account).strip('()'))
        fin.close()

        fin = open("terraform/terraform.tfvars", "wt")
        fin.write(data)
        fin.close()

    def execute(self):
        self.credentials()
        self.subscription_id()
        self.resource_group()
        time.sleep(10)
        self.storage_account()
        self.connect_str()
        self.storage_container()
        self.setup_backend()

if __name__ == "__main__":
    SetupAccount().execute()