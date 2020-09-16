from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2017_03_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2017_03_01.models import SecurityRule
from azure.mgmt.network.v2020_05_01.models import ApplicationSecurityGroup
from azure.mgmt.resource.resources import ResourceManagementClient

subscription_id = ''
credentials = ServicePrincipalCredentials(
    client_id = '',
    secret = '',
    tenant = ''
)

compute_client = ComputeManagementClient(credentials,subscription_id)
network_client = NetworkManagementClient(credentials,subscription_id)
resource_client = ResourceManagementClient(credentials,subscription_id)


resource_client.providers.register('Microsoft.Compute')
resource_client.providers.register('Microsoft.Network')

resource_group_name = 'Utsav-test'

parameters = NetworkSecurityGroup()
asg_parameters = ApplicationSecurityGroup()


parameters.location = 'UK South'
parameters.security_rules = [SecurityRule(protocol='Tcp',source_address_prefix='*',destination_address_prefix='*',source_port_range='*',destination_port_range='*',access='Allow',priority=101,direction='Inbound',name='NSG101')]   

asg_parameters.name = "test-asg"
asg_parameters.location = "UK South"
asg_parameters.id = "ID01"

network_client.network_security_groups.create_or_update(resource_group_name, "Utsav-test", parameters)
network_client.application_security_groups.create_or_update(resource_group_name,application_security_group_name=asg_parameters.name,parameters=asg_parameters)