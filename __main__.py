import pulumi
from pulumi_aws import ec2,rds
from decouple import config
import os

# Load environment variables from the .env file
region = config("AWS_REGION")
availability_zones = config("AWS_AVAILABILITY_ZONES").split(",")
num_public_subnets = int(config("MY_PUBLIC_SUBNETS"))
num_private_subnets = int(config("MY_PRIVATE_SUBNETS"))
vpc_cidr_prefix = config("MY_VPC_CIDR_PREFIX")
vpc_name = config("MY_VPC_NAME")
subnet_public_name = config("MY_SUBNET_PUBLIC_NAME")
subnet_private_name = config("MY_SUBNET_PRIVATE_NAME")
public_route_table = config("MY_PUBLIC_ROUTE_TABLE")
private_route_table = config("MY_PRIVATE_ROUTE_TABLE")
public_subnet_connect = config("MY_PUBLIC_SUBNET_CONNECT")
private_subnet_connect = config("MY_PRIVATE_SUBNET_CONNECT")
internet_gateway = config("MY_INTERNET_GATEWAY")
public_route = config("MY_PUBLIC_ROUTE")
public_route_cidr_des = config("MY_PUBLIC_ROUTE_CIDR_DES")
instance_type = config("Instance_Type")
ami = config("AMI")

# Create a VPC
vpc = ec2.Vpc(
    vpc_name,
    cidr_block=vpc_cidr_prefix,
    instance_tenancy="default",
    tags={
        "Name": vpc_name,
    },
)

public_subnets = []
private_subnets = []

# Create public and private subnets
for i in range(num_public_subnets):
    subnet_name = f"{subnet_public_name}{i + 1}"
    subnet = ec2.Subnet(
        subnet_name,
        vpc_id=vpc.id,
        availability_zone=region+availability_zones[i % len(availability_zones)],  # Rotate AZs
        cidr_block=f"10.0.{i + 1}.0/24",
        map_public_ip_on_launch=True,
        tags={
            "Name": subnet_name,
        },
    )
    public_subnets.append(subnet)

for i in range(num_private_subnets):
    subnet_name = f"{subnet_private_name}{i + 1}"
    subnet = ec2.Subnet(
        subnet_name,
        vpc_id=vpc.id,
        availability_zone=region+availability_zones[i % len(availability_zones)],  # Rotate AZs
        cidr_block=f"10.0.{num_public_subnets + i + 1}.0/24",
        tags={
            "Name": subnet_name,
        },
    )
    private_subnets.append(subnet)

# Create route tables
public_route_table = ec2.RouteTable(
    public_route_table,
    vpc_id=vpc.id,
    tags={
        "Name": public_route_table,
    },
)

private_route_table = ec2.RouteTable(
    private_route_table,
    vpc_id=vpc.id,
    tags={
        "Name": private_route_table,
    },
)

public_route_table_associations = []
private_route_table_associations = []

# Associate public subnets with the public route table
for i, subnet in enumerate(public_subnets):
    association = ec2.RouteTableAssociation(
        f"{public_subnet_connect}{i + 1}",
        subnet_id=subnet.id,
        route_table_id=public_route_table.id,
    )
    public_route_table_associations.append(association)

# Associate private subnets with the private route table
for i, subnet in enumerate(private_subnets):
    association = ec2.RouteTableAssociation(
        f"{private_subnet_connect}{i + 1}",
        subnet_id=subnet.id,
        route_table_id=private_route_table.id,
    )
    private_route_table_associations.append(association)

# Create an Internet Gateway
internet_gateway = ec2.InternetGateway(
    internet_gateway,
    vpc_id=vpc.id,
    tags={
        "Name": internet_gateway,
    },
)

# Create a public route in the public route table
public_route = ec2.Route(
    public_route,
    route_table_id=public_route_table.id,
    destination_cidr_block=public_route_cidr_des,
    gateway_id=internet_gateway.id,
)

app_security_group = ec2.SecurityGroup(
    "appSecurityGroup",
    vpc_id=vpc.id,
    ingress=[
        ec2.SecurityGroupIngressArgs(
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],  # Allow SSH from anywhere
        ),
        ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],  # Allow HTTP from anywhere
        ),
        ec2.SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],  # Allow HTTPS from anywhere
        ),
        # Add ingress rule for your application port here
        ec2.SecurityGroupIngressArgs(
            from_port=8000,
            to_port=8000,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={
        "Name": "appSecurityGroup",
    },
    
)

# Create a security group for RDS instances (Database Security Group)
db_security_group = ec2.SecurityGroup(
    "dbSecurityGroup",
    vpc_id=vpc.id,
    ingress=[
        ec2.SecurityGroupIngressArgs(
            from_port=5432,  # PostgreSQL port
            to_port=5432,
            protocol="tcp",
            security_groups=[app_security_group.id],  # Allow traffic from the application security group
        ),
    ],
    tags={
        "Name": "dbSecurityGroup",
    },
)

# Create an RDS parameter group for PostgreSQL
rds_parameter_group = rds.ParameterGroup(
    "postgres-parameter-group",
    family="postgres14",  # Use the appropriate PostgreSQL version (14 for example)
    parameters=[
        rds.ParameterGroupParameterArgs(
            name="autovacuum",
            value="on",
        ),
        # Add more PostgreSQL parameter settings as needed
    ],
)

# Subnet Group
rds_subnet_group = rds.SubnetGroup(
    "rds-subnet-group",
    subnet_ids=[subnet.id for subnet in private_subnets],  # Assuming private_subnets is a list of subnet objects
    tags={
        "Name": "RDS Subnet Group",
    },
)

# Create an RDS instance
rds_instance = rds.Instance(
    "rds-instance",
    allocated_storage=os.getenv('ALLOCATED_STORAGE'),  # Modify the storage size as needed
    storage_type=os.getenv('STORAGE_TYPE'),
    engine=os.getenv("ENGINE"),  # Use PostgreSQL
    engine_version=os.getenv("ENGINE_VERSION"),  # Specify the PostgreSQL version
    instance_class=os.getenv("INSTANCE_CLASS"),  # Choose an appropriate instance class
    username=os.getenv("USERNAME"),  # Master username
    password=os.getenv("PASSWORD"),  # Specify a strong master password
    skip_final_snapshot=True,  # Configure as needed
    vpc_security_group_ids=[db_security_group.id],  # Attach the database security group
    db_subnet_group_name=rds_subnet_group.name,  # Specify the name of your DB subnet group
    publicly_accessible=False,  # Disable public accessibility
    db_name=os.getenv("DB_NAME"),  # Specify the database name
    parameter_group_name=rds_parameter_group.name,  # Use the created parameter group
    multi_az=False, # Multi-AZ deployement
    tags={
        "Name": "RDSInstance",
    },
    
)

user_data = f"""
#!/bin/bash
sed -i 's/POSTGRES_USER ?= webapp/POSTGRES_USER ?= {os.getenv("USERNAME")}/g' /home/ec2-user/webapp/Makefile
sed -i 's/POSTGRES_PASSWORD ?= webapp/POSTGRES_PASSWORD ?= {os.getenv("PASSWORD")}/g' /home/ec2-user/webapp/Makefile
sed -i 's/POSTGRES_HOST ?= 127.0.0.1/POSTGRES_HOST ?= {rds_instance.address}/g' /home/ec2-user/webapp/Makefile
sed -i 's/POSTGRES_DB ?= webapp/POSTGRES_DB ?= {os.getenv("DB_NAME")}/g' /home/ec2-user/webapp/Makefile
"""

ec2_instance = ec2.Instance(
    "ec2Instance",
    instance_type=instance_type,
    ami=ami,  # Replace with your custom AMI ID
    vpc_security_group_ids=[app_security_group.id],
    subnet_id=public_subnets[0].id,  # Choose one of your public subnets
    root_block_device=ec2.InstanceRootBlockDeviceArgs(
        volume_size=25,
        volume_type="gp2",
    ),
    tags={
        "Name": "EC2Instance",
    },
    user_data_replace_on_change=True,
    user_data=user_data

)
