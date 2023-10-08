import ansible_creator
import subprocess
import os
import argparse

# Parsing command line parameters
parser = argparse.ArgumentParser(
    description="This scripts reads Files on extended DTDL and builds the digital parts of the DT of that definition.")

parser.add_argument("-i", "--inputPath", help="Path, in which the DTDL files are.")
parser.add_argument("-o", "--outputPath", help="The Path, in which the Ansible files will be written.")

args = parser.parse_args()
input_path = args.inputPath
output_path = args.outputPath

class ansibleRemoteObject:
    def __init__(self):
        return

def create_ansible_setup(input_path: str,
              playbookPath: str,
              inventoryPath: str,
              telegraf_conf_path: str,
              servicesPath: str):

    apb = ansible_creator.ansiblePlaybookDTDL()
    if os.path.isdir(input_path):
        apb.readFromPath(input_path)
    elif os.path.isfile(input_path):
        apb.readFromFile(input_path)
    else:
        print(f"{input_path} is neither directory or folder.")
    apb.savePlaybook(playbookPath, telegraf_conf_path, input_path, playbookPath, servicesPath)
    apb.saveInventoryFile(inventoryPath)
    
    apb.save_telegraf_configs(telegraf_conf_path)

def run_ansible_playbook(
        inventory_path: str,
        playbook_path : str):
    command = f"ansible-playbook -i {os.path.basename(inventory_path)} {os.path.basename(playbook_path)}"
    directory = os.path.dirname(playbook_path)
    result = subprocess.run(command, shell=True, cwd=directory)
    if result.returncode == 0:
        print("Ansible Playbook finished successfully")
    else:
        print(f"Running the Ansisble Playbook returned Code {result.returncode}")
    return result

# input_path = "../../../bsp_setup_presentation/dtdl/"
# output_path = "../../../bsp_setup_presentation/output/"


playbookPath = output_path + "playbook.yml"
inventoryPath = output_path + "inventory.ini"
telegraf_conf_path = output_path + "telegraf_configs/"
servicesPath = output_path + "services/"

create_ansible_setup(input_path,
          playbookPath,
          inventoryPath,
          telegraf_conf_path,
          servicesPath)
run_ansible_playbook(
    inventoryPath,
    playbookPath)