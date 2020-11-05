import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource.resources import ResourceManagementClient

def CreateAzureCredentials():
    """
    Get Azure Credentals which will be used to create Management Clients. The Service Principal is picked up from config.json file
    """
    with open('config.json') as config_file:
        data = json.load(config_file)
    credentials = ServicePrincipalCredentials(client_id = data['client_id'],secret = data['client_secret'],tenant = data['tenantId'])
    subscriptionId = data['subscriptionId']
    return credentials,subscriptionId

def main():
    RESOURCE_GROUP_NAME = "VM-Test-RG"
    LOCATION = "centralus"
    VNET_NAME = "python-vnet"
    SUBNET_NAME = "python-subnet"
    IP_NAME = "python-ip"
    IP_CONFIG_NAME = "python-ip-config"
    NIC_NAME = "python-nic"
    VM_NAME = "ExampleVM"
    USERNAME = "azureuser"
    PASSWORD = "ChangePa$$w0rd24"
    credentials,subscriptionId = CreateAzureCredentials()
    network_client = NetworkManagementClient(credentials,subscriptionId)
    resource_client = ResourceManagementClient(credentials, subscriptionId)
    compute_client = ComputeManagementClient(credentials, subscriptionId)
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
    )
    print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")
    poller = network_client.virtual_networks.create_or_update(RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": LOCATION,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
    )
    vnet_result = poller.result()
    print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")
    poller = network_client.subnets.create_or_update(RESOURCE_GROUP_NAME, 
        VNET_NAME, SUBNET_NAME,
        { "address_prefix": "10.0.0.0/24" }
    )
    subnet_result = poller.result()
    print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
    poller = network_client.public_ip_addresses.create_or_update(RESOURCE_GROUP_NAME,
        IP_NAME,
        {
            "location": LOCATION,
            "sku": { "name": "Standard" },
            "public_ip_allocation_method": "Static",
            "public_ip_address_version" : "IPV4"
        }
    )
    ip_address_result = poller.result()
    print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")
    poller = network_client.network_interfaces.create_or_update(RESOURCE_GROUP_NAME,
        NIC_NAME, 
        {
            "location": LOCATION,
            "ip_configurations": [ {
                "name": IP_CONFIG_NAME,
                "subnet": { "id": subnet_result.id },
                "public_ip_address": {"id": ip_address_result.id }
            }]
        }
    )
    nic_result = poller.result()
    print(f"Provisioned network interface client {nic_result.name}")
    print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")
    poller = compute_client.virtual_machines.create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "publisher": 'Canonical',
                    "offer": "UbuntuServer",
                    "sku": "16.04.0-LTS",
                    "version": "latest"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": VM_NAME,
                "admin_username": USERNAME,
                "admin_password": PASSWORD
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_result.id,
                }]
            }
        }
    )
    vm_result = poller.result()
    print(f"Provisioned virtual machine {vm_result.name}")

    
if __name__ == "__main__":
    main()