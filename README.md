# Ansible_RunvROWorkflow
Run VMware vRO workflow from ansible playbook.
A custom Ansible module run_vro_wf is provided in library folder.

---
***Module Inputs:***
-	vro_server: vRealize Orchestrator IP or FQDN & Port 8281 or 443 if embeded in vRA
-	username: vRealize Orchestrator user name
-	password: vRealize Orchestrator password 
-	workflow_id: Id of the workflow to run. Must be copy form vRO.
-       input_values: All workflow input values in YAML object format:
```
        Ansible:
                Input1_name: value
                Input2_name: value
                Input3_name:
                - Array_value1
                - Array_value2
                - Array_value3
```
Inputs must much vRO workflow inputs

---
***Remark:***
For Annsible --check flag functionality to work a test input in vRO workflow is mandatory but is hidden from ansible perspective and must be omitted in input_valuse section of the playbook. 
This value is used when ansible-playbook is run with --check flag.
Test implementation is dependent on vRO WF functionality.
