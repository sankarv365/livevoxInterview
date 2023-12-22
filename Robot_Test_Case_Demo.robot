*** Settings ***
Library          liveVox.py

*** Variables ***
${ASGName}       lv-test-cpu


*** Test Cases ***
ASG_Test_001
    [Documentation]    This Test Verifies the ASG Instances and It's details
    ${ASG_Details} =    precondition steps    ${ASGName}
    verify desired count with running instance    ${ASG_Details}[0]    ${ASG_Details}[1]    ${ASG_Details}[2]
    verify availability zones are distributed    ${ASG_Details}[1]    ${ASG_Details}[2]
    verify SecuirtyGroup ImageID VPCID    ${ASG_Details}[3]
    Check Longest Running Instance     ${ASG_Details}[4]

ASG_Test_002
    [Documentation]    This Test Verifies the ASG schedules
    ${time_elapsed} =   get next scheduled action    ${ASGName}
    Log   The next instance will run in : ${time_elapsed}
    Check Instance State


*** Keywords ***
Check Longest Running Instance
    [Arguments]    ${instance_up_time_list}
    ${longest_running_instance}    ${run_time} =    check uptime of ASG running instances     ${instance_up_time_list}
    Log   Longest Running Instance is: ${longest_running_instance} and it's Run time is: ${run_time}

Check Instance State
    ${launch_count}   ${termination_count} =    get instances launched terminated    ${ASGName}
    Log   Total instances launched today: ${launch_count}
    Log   Total instances terminated today: ${termination_count}