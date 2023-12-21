import boto3
import os
import sys
from datetime import datetime, timezone

aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']


def get_asg_describe(asg_name):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    return asg_response


def verify_desired_count_with_running_instance(desired_capacity,running_instances,az_counts):
    print("Desired Capacity is:",desired_capacity)
    print("Total Running Instances:",running_instances)
    assert desired_capacity == running_instances, "Instance Count is Mismatch with Desired Count"
    print("Instance Count is matching with Desired Count")


def verify_availability_zones_are_distributed(running_instances,az_counts):
    if running_instances > 1:
        assert running_instances == len(az_counts), "Availability Zone is not Unique for the Running Instance"
    print("Availability Zone is Unique for the Running Instance, so it is distributed",az_counts)


def verify_SecuirtyGroup_ImageID_VPCID(other_info):
    value_list_to_check = list(other_info.values())
    print(value_list_to_check[0])
    for values in other_info.values():
        print(values)
        assert value_list_to_check[0] == values, "SecuirtyGroup, ImageID and VPCID Is not matching"
    print("Verified all Instance has the same: SecuirtyGroup, ImageID and VPCID")


def check_uptime_of_ASG_running_instances(instance_up_time_list):
    print(instance_up_time_list)
    longest_running_instance = None
    longest_uptime = None
    for instance_item in instance_up_time_list:
        uptime = instance_up_time_list[instance_item]
        if longest_uptime is None or uptime > longest_uptime:
            longest_uptime = uptime
            longest_running_instance = instance_item
    return longest_running_instance

def get_instance_details(asg_response):
    instances = asg_response['AutoScalingGroups'][0]['Instances']
    instance_ids = [instance['InstanceId'] for instance in instances]
    print(instance_ids)
    ec2_client = boto3.client('ec2',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    instance_response = ec2_client.describe_instances(InstanceIds=instance_ids)
    return instance_response

def precondition_steps(asg_name):
    asg_response=get_asg_describe(asg_name)
    desired_capacity = asg_response['AutoScalingGroups'][0]['DesiredCapacity']
    print("Desired Capacity of the ASG is : ", desired_capacity)
    instance_response=get_instance_details(asg_response)
    running_instances = 0
    az_counts = {}
    other_info = {}
    instance_up_time = {}
    for reservation in instance_response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                running_instances+=1
            else:
                continue
            az = instance['Placement']['AvailabilityZone']
            if az in az_counts:
                az_counts[az] += 1
            else:
                az_counts[az] = 1
            instance_id = instance['InstanceId']
            security_groups = [sg['GroupId'] for sg in instance['SecurityGroups']]
            image_id = instance['ImageId']
            vpc_id = instance['VpcId']
            other_info[instance_id]=[security_groups,image_id,vpc_id]
            uptime = get_instance_uptime(instance)
            print(f"Instance ID: {instance['InstanceId']}, Uptime: {uptime}")
            instance_up_time[instance_id]=uptime
    instance_info=[desired_capacity,running_instances, az_counts,other_info,instance_up_time]
    return instance_info


def get_instance_uptime(instance):
    launch_time = instance['LaunchTime']
    current_time = datetime.now(timezone.utc)
    uptime = current_time - launch_time
    return uptime


def calculate_elapsed_time(start_time):
    current_time = datetime.utcnow()
    elapsed_time = current_time - start_time
    elapsed_seconds = elapsed_time.total_seconds()
    hours = int(elapsed_seconds // 3600)
    minutes = int((elapsed_seconds % 3600) // 60)
    seconds = int(elapsed_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_next_scheduled_action(asg_name):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    response = asg_client.describe_scheduled_actions(AutoScalingGroupName=asg_name)
    if 'ScheduledUpdateGroupActions' in response:
        # Sort scheduled actions by time and find the next one to execute
        scheduled_actions = response['ScheduledUpdateGroupActions']
        scheduled_actions.sort(key=lambda x: x['StartTime'])
        for action in scheduled_actions:
            start_time = action['StartTime']
            start_time = start_time.utcnow()
            current_time = datetime.utcnow()
            if start_time > current_time:
                time_until_action = calculate_elapsed_time(start_time)
                return time_until_action
    return "No Instance is Scheduled"


def get_instances_launched_terminated(asg_name):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    response = asg_client.describe_auto_scaling_instances()
    instances_launched = 0
    instances_terminated = 0
    for instance in response['AutoScalingInstances']:
        if instance['AutoScalingGroupName'] ==asg_name:
            if instance['LifecycleState'] == 'InService':
                instances_launched+=1
            elif instance['LifecycleState'] == 'Terminated':
                instances_terminated+=1
    return instances_launched, instances_terminated


def main(argv):
    print(sys.argv)
    if len(sys.argv)>1:
        response=get_asg_describe(str(sys.argv[1]))
        print(response)
    else:
        print("Please pass correct arguments")
        print("Usage ./sample-test.py asg_name")


if __name__ == "__main__":
    main(sys.argv)
