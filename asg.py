#Import Statements
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network.v2020_06_01._network_management_client import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models._models_py3 import SecurityRule,ApplicationSecurityGroup,NetworkSecurityGroup


def CreateAzureCredentials():
    """
    Get Azure Credentals which will be used to create Management Clients. The Service Principal is picked up from config.json file
    """
    with open('config.json') as config_file:
        data = json.load(config_file)
    credentials = ServicePrincipalCredentials(client_id = data['client_id'],secret = data['client_secret'],tenant = data['tenantId'])
    subscriptionId = data['subscriptionId']
    return credentials,subscriptionId

def CreateManagementClients(credentials,subscriptionId):
    """
    Create Network Client to handle ASG and NSG
    """
    network_client = NetworkManagementClient(credentials,subscriptionId)
    return network_client

def CreateASGParameters(location,name):
    """
    Create parameters which will be used to create new ASG
    """
    asg_parameters = ApplicationSecurityGroup()
    asg_parameters.name = name
    asg_parameters.location = location
    return asg_parameters

def CreateNewASG(network_client,asg_parameters,resource_group_name):
    """
    Create/Update ASG using the parameters and network client. If the ASG Name exists in the Resource group the ASG will be updated with new rules if any.
    """
    asg_create_async = network_client.application_security_groups.create_or_update(resource_group_name,application_security_group_name=asg_parameters.name,parameters=asg_parameters)
    asg_create_async.wait()
    asg = network_client.application_security_groups.get(resource_group_name,asg_parameters.name,raw=False)
    return asg

def CreateNSGSecurityRule(asg):
    """
    Create NSG security rule which includes the new ASG which was created
    """
    #NSG Parameters for the security rule. These can be changed as per the application.
    protocol = 'Tcp'
    source_application_security_groups = [asg]
    destination_address_prefix = '*'
    source_port_range = '*'
    destination_port_range = '*'
    priority = '103'
    direction = 'Inbound'
    name_of_rule = 'Sample_Rule'
    access = 'Allow'
    security_rule = SecurityRule(protocol=protocol,
                                destination_address_prefix=destination_address_prefix,
                                source_port_range=source_port_range,
                                destination_port_range=destination_port_range,
                                source_application_security_groups=source_application_security_groups,
                                access=access,
                                priority=priority,
                                direction=direction,
                                name=name_of_rule)
    return security_rule

def UpdateNSG(name_of_nsg,resource_group_name,network_client,security_rule):
    """
    Update NSG using the parameters and network client. This function assumes we have a NSG with the name 'name_of_nsg' in the provided resource group
    """
    nsg = network_client.network_security_groups.get(resource_group_name,name_of_nsg)
    nsg.security_rules.append(security_rule)
    nsg_update_async = network_client.network_security_groups.create_or_update(resource_group_name,name_of_nsg,nsg)
    nsg_update_async.wait()

def CreateNSG(name_of_nsg,resource_group_name,location,network_client):
    """
    Function to create new NSG. The security rules has to be defined in the function by updating the location and security rules parameters
    """
    nsg_parameters = NetworkSecurityGroup()
    nsg_parameters.location = location
    #We can add multiple rules in the security_rules list
    nsg_parameters.security_rules = [SecurityRule(protocol='Tcp',source_address_prefix='*',destination_address_prefix='*',source_port_range='*',destination_port_range='*',access='Allow',priority=101,direction='Inbound',name='NSG101')]   
    nsg = network_client.network_security_groups.create_or_update(resource_group_name,name_of_nsg,nsg_parameters)

def main():
    asg_location = 'Central US'
    asg_name = 'Sample-Asg'
    resource_group_name = 'sample-RG'
    name_of_nsg = 'vm-test-nsg'
    credentials,subscriptionId = CreateAzureCredentials()
    network_client = CreateManagementClients(credentials,subscriptionId)
    asg_parameters = CreateASGParameters(asg_location,asg_name)
    asg = CreateNewASG(network_client,asg_parameters,resource_group_name)
    security_rule = CreateNSGSecurityRule(asg)
    #To create a new nsg uncomment the below line
    #CreateNSG(name_of_nsg,resource_group_name,network_client)
    UpdateNSG(name_of_nsg,resource_group_name,network_client,security_rule)
    
if __name__ == "__main__":
    main()