from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network.v2020_06_01._network_management_client import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models._models_py3 import NetworkSecurityGroup,SecurityRule,ApplicationSecurityGroup
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.compute.v2020_06_01 import ComputeManagementClient

subscription_id = ''
credentials = ServicePrincipalCredentials(
    client_id = '',
    secret = '',
    tenant = ''
)

compute_client = ComputeManagementClient(credentials,subscription_id)
network_client = NetworkManagementClient(credentials,subscription_id)
resource_client = ResourceManagementClient(credentials,subscription_id)

NSG_Parameters = NetworkSecurityGroup()
resource_group_name = 'Utsav-test'
nsg_name = 'vm-test-nsg'

#Create a new ASG (parameters)
asg_parameters = ApplicationSecurityGroup()
asg_parameters.name = "test-asg"
asg_parameters.location = "Central US"
# asg_parameters.id = "ID01"


#Create a new ASG
asg_create_async = network_client.application_security_groups.create_or_update(resource_group_name,application_security_group_name=asg_parameters.name,parameters=asg_parameters)
asg_create_async.wait()

#if we want to use existing asg we will use this. Prefer using this even after creating new ASG to prevent object missmatch
asg = network_client.application_security_groups.get(resource_group_name,asg_parameters.name,raw=False)

#Define new security rules
security_rules = SecurityRule(protocol='Tcp',destination_address_prefix='*',source_port_range='*',destination_port_range='*',source_application_security_groups=[asg],access='Allow',priority=103,direction='Inbound',name='NSG103')

#Define new parameters for NSG
NSG_Parameters.location = 'Central US'
NSG_Parameters.security_rules = [security_rules]

nsg = network_client.network_security_groups.get(resource_group_name,'vm-test-nsg')
nsg.security_rules.append(security_rules) #Append new security rules which include nsg (This operation was made by looking at the response of above line)

#Update NSG with new Parameters
nsg_update_async = network_client.network_security_groups.create_or_update(resource_group_name,nsg_name,nsg)
nsg_update_async.wait()


