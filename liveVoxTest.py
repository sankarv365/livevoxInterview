import boto3
import os
import sys


aws_access_key_id=os.environ['aws_access_key_id']
aws_secret_access_key=os.environ['aws_secret_access_key']


def get_asg_describe(asgname):
    asg_client = boto3.client('autoscaling',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key,region_name='ap-south-1')
    asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asgname])
    return asg_response



def main(argv):
    print(sys.argv)
    if len(sys.argv)>1:
        response=get_asg_describe(str(sys.argv[1]))
        print(response)
    else:
        print("Please pass correct arguments")
        print("Usage ./sample-test.py asgname")


if __name__ == "__main__":
    main(sys.argv)
