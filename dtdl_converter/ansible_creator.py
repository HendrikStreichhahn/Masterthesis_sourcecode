import json
import uuid
import glob
import os
import string_helper
import telegraf_creator

remote_telegraf_conf_path = "/dt/telegraf.conf"

class sshInfoClass:
    def __init__(self,
            address: str,
            sshUser: str,
            port: int = 22,
            password: str = "", 
            certificate: str = ""):
        self.address=address
        self.sshUser = sshUser
        self.port = port
        if password != "":
            self.password = password
        if certificate != "":
            self.certificate = certificate

class fileTransmissionCommand:
    def __init__(self,
                 source:str,
                 dest: str,
                 mode: str = string_helper.UNDEFINED_STRING):
        self.source = source
        self.dest = dest
        self.mode = mode

class command:
    def __init__(self,
                 command: str,
                 parameters: str,
                 type: str):
        self.command = command
        self.parameters = parameters
        self.type = type

def writeServiceFile(outputFile: str,
            execStart: str,
            restart: str = "always",
            description: str = "Service",
            user: str = "root",
            group: str = "root"):
        res = ""
        res = string_helper.addLine(res, "[Unit]")
        res = string_helper.addLine(res, f"Description={description}")
        res = string_helper.addLine(res, "[Service]")
        res = string_helper.addLine(res, f"ExecStart={execStart}")
        res = string_helper.addLine(res, f"Restart={restart}")
        res = string_helper.addLine(res, f"User={user}")
        res = string_helper.addLine(res, f"Group={group}")
        res = string_helper.addLine(res, f"[Install]")
        res = string_helper.addLine(res, f"WantedBy=multi-user.target")
        folder = os.path.dirname(outputFile)
        if not os.path.exists(folder):
            make_res = os.makedirs(folder)
            #print(make_res)
        with open(outputFile, "w") as file:
            file.write(res)


class requiredPackage:
    def __init__(self,
                 name: str,
                 source: str):
        self.name = name
        self.source = source

class ansibleInfoDTDLInstance:
    def __init__(self):
        self.instanceID: str = ""
        self.sshInfos: sshInfoClass
        self.fileTransmissionCommands: list([fileTransmissionCommand]) = []
        self.commands:  list([command]) = []
        self.requiredPackages: list([requiredPackage]) = []
        self.addTelegrafAptPrerequisitedPackages()
        self.telegraf_config_file_added = False
        self.add_telegraf_start_command()
        
    
    def getInventoryString(self,
                           indentationChar: str = "  ",
                           indentationCount: int = 0,
                           outputPath: str = "/"):
        indentString = string_helper.char_n_times(indentationCount,
                                    indentationChar)
        result = indentString + "[" + string_helper.cleanify_string(self.instanceID) + "_grp]"

        stringToAdd = (indentString + string_helper.cleanify_string(self.instanceID) + 
                       " ansible_ssh_user=" + self.sshInfos.sshUser +
                       " ansible_host=" + self.sshInfos.address)
        if hasattr(self.sshInfos, 'port') and self.sshInfos.port != "":
            stringToAdd = stringToAdd + " ansible_port=" + str(self.sshInfos.port)
        if hasattr(self.sshInfos, 'password'):
            stringToAdd = stringToAdd + " ansible_password=" + self.sshInfos.password
        if hasattr(self.sshInfos, 'certificate'):
            stringToAdd = stringToAdd + " ansible_ssh_private_key_file=" + string_helper.make_relative_path(outputPath, self.sshInfos.certificate)
        stringToAdd = stringToAdd + " ansible_ssh_args=\"-o StrictHostKeyChecking=no\""
        result = string_helper.addLine(result, stringToAdd)
        return result
    
    def getPackageSourceUpdateTasks(self,
                        indentationChar: str = "  ",
                        indentationCount: int = 0):
        aptUpdateRequired= False
        for reqPack in self.requiredPackages:
            if reqPack.source == "apt":
                aptUpdateRequired = True
        result = ""
        if (aptUpdateRequired):
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: Update apt package cache")
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.apt:")
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "update_cache: yes")
            result = string_helper.addLine(result, "")
        return result
    
    def getInstallPackagesTasks(self,
                        indentationChar: str = "  ",
                        indentationCount: int = 0):
        result = ""
        for reqPack in self.requiredPackages:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: Install " + reqPack.name)
            if reqPack.source == "apt":
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.apt:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "name: " + reqPack.name)
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: present")
            else:
                print(f"Invalid Packagesource: {reqPack.source}")
            result = string_helper.addLine(result, "")
        return result
    
    def getFileTransmissionTasks(self,
                        indentationChar: str = "  ",
                        indentationCount: int = 0,
                        outputPath = "/"):
        result = ""
        for fileTransmission in self.fileTransmissionCommands:
            #create destination folder, if not exists
            folder = os.path.dirname(fileTransmission.dest)
            if (folder != ""):
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: Create folder " + folder)
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.file:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "path: " + folder)
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: directory")
            

            # Copy File
            #sourcePath = string_helper.make_relative_path(outputPath, fileTransmission.source)
            sourcePath = fileTransmission.source
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: Copy file " + fileTransmission.source)
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.copy:")
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "src: " + sourcePath)
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "dest: " + fileTransmission.dest)
            if (fileTransmission.mode != string_helper.UNDEFINED_STRING):
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "mode: " + fileTransmission.mode)
            result = string_helper.addLine(result, "")

            #print(f"AbsPath: {fileTransmission.source}")
            #print(f"RelPath: {string_helper.path_remove_front(string_helper.make_relative_path(outputPath, fileTransmission.source))}")
            #print("---")
        return result
    
    def systemd_reread_required(self)-> bool:
        for command in self.commands:
            if command.type == "command_as_service_start" or command.type == "command_as_service_stopped":
                return True
        return False
    
    def getBashCommandTasks(self,
                        indentationChar: str = "  ",
                        indentationCount: int = 0):
        # TODO Handle execMoment
        # TODO Service hinzugügen
        result = ""
        # if self.systemd_reread_required():
        #     result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + f"- name: Reload Systemd services")
        #     result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"systemd:")
        #     result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + f"state: reloaded")
        for i, command in enumerate(self.commands):
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + f"- name: Run Command {i}")
            args = ""
            if command.parameters != string_helper.UNDEFINED_STRING:
                for arg in command.parameters:
                    args = args + " " + arg
            if command.type == string_helper.UNDEFINED_STRING:
                print("command.type not defined. Type \"once\" is assumed")
            if command.type == "once" or command.type == string_helper.UNDEFINED_STRING:
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) +
                    "ansible.builtin.shell: \"" + command.command + args + "\"")
            elif command.type == "once_no_wait":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) +
                    "ansible.builtin.shell: \"" + command.command + args + "\"")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "async: 36000")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "poll: 0")
            elif command.type == "service_start":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.service:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + f"name: {command.command}")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "daemon_reload: true")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: restarted")
            elif command.type == "service_stop":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.service:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + f"name: {command.command}")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "daemon_reload: true")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: stopped")
            elif command.type == "command_as_service_start":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.service:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + f"name: {string_helper.get_service_file_name(self.instanceID, i)}")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "daemon_reload: true")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: restarted")
            elif command.type == "command_as_service_stop":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) + "ansible.builtin.service:")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + f"name: {string_helper.get_service_file_name(self.instanceID, i)}")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "daemon_reload: true")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "state: stopped")
            elif command.type == "on_update":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) +
                    "ansible.builtin.shell: \"" + command.command + args + "\"")
            elif command.type == "on_update_nowait":
                result = string_helper.addLine(result,
                    string_helper.char_n_times(indentationCount+1, indentationChar) +
                    "ansible.builtin.shell: \"" + command.command + args + "\"")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "async: 36000")
                result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "poll: 0")
            else:
                raise ValueError(f"wrong command.type: {command.type} is unknown.")
        return result
    
    def generateCommandAsServiceFiles(self,
                                      servicesFolder: str):
        for i, command in enumerate(self.commands):
            if command.type == "command_as_service_start" or command.type == "command_as_service_stop":
                args = ""
                if command.parameters != string_helper.UNDEFINED_STRING:
                    for arg in command.parameters:
                        args = args + " " + arg
                writeServiceFile(servicesFolder + string_helper.get_service_file_name(self.instanceID, i),
                                 command.command + args)
                localPath = string_helper.get_abs_path(servicesFolder + string_helper.get_service_file_name(self.instanceID, i), __file__)
                self.fileTransmissionCommands.append(
                    fileTransmissionCommand(localPath,
                                            f"/etc/systemd/system/{string_helper.get_service_file_name(self.instanceID, i)}",
                                            "o+rwx"))
        
    def getTasksString(
            self,
            telegraf_config_path: str,
            dtdl_file_path: str,
            playbookpath: str,
            indentationChar: str = "  ",
            indentationCount: int = 0):
        folder, _ = os.path.split(dtdl_file_path)
        if not self.telegraf_config_file_added:
            self.add_telegraf_conf_filetransmissions(dtdl_file_path, telegraf_config_path)
            self.telegraf_config_file_added = True
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: " + self.instanceID)
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "hosts: " + string_helper.cleanify_string(self.instanceID))
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "become: yes")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "tasks:")
        result = string_helper.addLine(result, self.getPackageSourceUpdateTasks(indentationChar, indentationCount + 2))
        result = string_helper.addLine(result, self.getInstallPackagesTasks    (indentationChar, indentationCount + 2))
        result = string_helper.addLine(result, self.getTelegrafInstallTasks    (indentationChar, indentationCount + 2))
        result = string_helper.addLine(result, self.getFileTransmissionTasks   (indentationChar, indentationCount + 2, outputPath=playbookpath))
        result = string_helper.addLine(result, self.getBashCommandTasks        (indentationChar, indentationCount + 2))
        return result
    
    def readInstanceFromFile(self, path: str):
        with open(path, "r") as file:
            fileContentJson = json.load(file)
            self.readInstanceFromJson(
                fileContentJson,
                path)

    def readInstanceFromJson(self, jsonDef: json, base_path: str):
        if "@type" not in jsonDef:
            raise ValueError("'@type' not found.")
        if not (jsonDef["@type"] == "Instance"):
            raise ValueError("'@type' must be 'Instance'")
        if "@id" not in jsonDef:
            self.instanceID = str(uuid.uuid4())
        else:
            self.instanceID = jsonDef["@id"]
        
        self.telegraf_conf = telegraf_creator.telegraf_config()

        if "contents" in jsonDef:
            for content in jsonDef["contents"]:
                contentTypeKnown = False
                if "@type" not in content:
                   raise ValueError(f"'@type' not found in {content}")
                typeString = content["@type"]
                if "@id" in content:
                    content_id = content["@id"]
                else:
                    content_id = str(uuid.uuid4())
                if typeString == "InstanceTelemetry":
                    contentTypeKnown = True
                    if "realization" in content:
                        self.telegraf_conf.add_telemetry_realization(content_id, content["realization"])
                    else:
                        raise ValueError(f"{content} must contain 'realization'")
                if typeString == "InstanceCommand":
                    contentTypeKnown = True
                    if "request" in content:
                        if "realization" in content["request"]:
                            if "@id" in content["request"]:
                                realization_id = content["request"]["@id"]
                            else:
                                realization_id = str(uuid.uuid4())
                            self.telegraf_conf.add_telemetry_realization(realization_id, content["request"]["realization"])
                        else:
                            raise ValueError(f"{content}.realization must contain 'realization'")
                    else:
                        print("Warning: No Request defined in CommandRealization. The Command is not callable.")
                    if "response" in content:
                        if "realization" in content["response"]:
                            if "@id" in content["response"]:
                                realization_id = content["response"]["@id"]
                            else:
                                realization_id = str(uuid.uuid4())
                            self.telegraf_conf.add_telemetry_realization(realization_id, content["response"]["realization"])
                        else:
                            raise ValueError(f"{content}.realization must contain 'realization'")
                    # if "realization" in content:
                    #     self.telegraf_conf.add_telemetry_realization(telemId, content["realization"])
                    # else:
                    #     raise ValueError(f"{content} must contain 'realization'")
                if typeString == "TelemetryConnector":
                    contentTypeKnown = True
                    self.telegraf_conf.add_telemetry_connector(content)
                if not contentTypeKnown:
                    print(f"Unknown content Type {typeString}")
                # TODO

        # TODO extends
        if "extends" in jsonDef:
            raise ValueError("'extends' is not implemented.")

        if "sshConnection" not in jsonDef:
            raise ValueError("'sshConnection' not found.")
        else:
            if "address" not in jsonDef["sshConnection"]:
                raise ValueError("'sshConnection.address' not found.")
            else:
                address = jsonDef["sshConnection"]["address"]
            if "sshUser" not in jsonDef["sshConnection"]:
                raise ValueError("'sshConnection.sshUser' not found.")
            else:
                user = jsonDef["sshConnection"]["sshUser"]
            if "port" in jsonDef["sshConnection"]:
                port = jsonDef["sshConnection"]["port"]
            else:
                port = ""
            if "password" in jsonDef["sshConnection"]:
                password = jsonDef["sshConnection"]["password"]
            else:
                password = ""
            if "certificate" in jsonDef["sshConnection"]:
                cert_path = jsonDef["sshConnection"]["certificate"]
                certificate = string_helper.get_abs_path(cert_path, base_path)
            else:
                certificate = ""
            if "password" not in jsonDef["sshConnection"] and "certificate" not in jsonDef["sshConnection"]:
                raise ValueError("'sshConnection.password' or 'sshConnection.certificate' must be given.")
            self.sshInfos = sshInfoClass(address,
                user,
                port,
                password, 
                certificate)
        
        if "fileTransmissions" in jsonDef:
            for content in jsonDef["fileTransmissions"]:
                if "source" not in content:
                    raise ValueError(f"'source' not found in {content}")
                else:
                    inpPath = content["source"]
                    absPath = string_helper.get_abs_path(inpPath, base_path)
                    source = absPath
                if "destination" not in content:
                    raise ValueError(f"'destination' not found in {content}")
                else:
                    destination = content["destination"]
                if "mode" in content:
                    mode = content["mode"]
                else:
                    mode = string_helper.UNDEFINED_STRING
                self.fileTransmissionCommands.append(fileTransmissionCommand(source, destination, mode))
        
        if "commands" in jsonDef:
            for content in jsonDef["commands"]:
                if "command" not in content:
                    raise ValueError(f"'command' not found in {content}")
                else:
                    commandStr = content["command"]
                if "parameters" in content:
                    parameters = content["parameters"]
                else:
                    parameters = string_helper.UNDEFINED_STRING
                if "type" in content:
                    type = content["type"]
                else:
                    type = string_helper.UNDEFINED_STRING
                self.commands.append(command(commandStr, parameters, type))
        
        if "requiredPackages" in jsonDef:
            for content in jsonDef["requiredPackages"]:
                if "name" not in content:
                    raise ValueError(f"'name' not found in {content}")
                else:
                    name = content["name"]
                if "source" not in content:
                    raise ValueError(f"'source' not found in {content}")
                else:
                    source = content["source"]
                self.requiredPackages.append(requiredPackage(name, source))

    def addTelegrafAptPrerequisitedPackages(self):
        self.requiredPackages.append(requiredPackage("curl", "apt"))
        self.requiredPackages.append(requiredPackage("apt-transport-https", "apt"))
        self.requiredPackages.append(requiredPackage("software-properties-common", "apt"))
    
    def getTelegrafInstallTasks(self,
                                    indentationChar: str = "  ",
                                    indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "- name: Install telegraf")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "shell: |")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "wget -q https://repos.influxdata.com/influxdata-archive_compat.key")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | tee /etc/apt/sources.list.d/influxdata.list")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+2, indentationChar) + "apt update && apt install telegraf -y")
        result = string_helper.addLine(result, "")
        return result
    
    def add_telegraf_conf_filetransmissions(
            self,
            base_path: str,
            telegraf_config_folder: str):
        #telegraf_config_folder_prior = telegraf_config_folder
        #telegraf_config_folder = string_helper.path_remove_front(telegraf_config_folder)
        
        # absPath = string_helper.get_abs_path(
        #                 telegraf_config_folder,
        #                 base_path)
        absPath = string_helper.get_abs_path(telegraf_config_folder)
        telegraf_path = self.get_telegraf_config_path(absPath)
        self.fileTransmissionCommands.append(
            fileTransmissionCommand(
                telegraf_path,
                "/telegraf_conf/remote_telegraf.conf",
                "o+rw"))
    
    def add_telegraf_start_command(self):
        self.commands.append(command("telegraf --config /telegraf_conf/remote_telegraf.conf", "", "command_as_service_start"))

    def save_telegraf_config(self,
                             folder: str):
        self.telegraf_conf.save_to_file(self.get_telegraf_config_path(folder))
    
    def get_telegraf_config_path(self, folder: str):
        if folder.endswith('/'):
            res =  f"{folder}telegraf_{string_helper.cleanify_string(self.instanceID)}.conf"
        else:
            res =  f"{folder}/telegraf_{string_helper.cleanify_string(self.instanceID)}.conf"
        return res


class ansiblePlaybookDTDL:
    instances : list([ansibleInfoDTDLInstance])= []
    def __init__(self):
        return

    def readFromPath(self, path: str):
        file_list = glob.glob(f"{path}/*.dtdl")
        if len(file_list) == 0:
            raise ValueError(f"No *.dtdl files found in \"{path}\"")
        for filename in file_list:
            instance = ansibleInfoDTDLInstance()
            instance.readInstanceFromFile(filename)
            self.instances.append(instance)
    
    def readFromFile(self, path: str):
        try:
            with open(path, 'r') as file:
                file_content = json.load(file)
                for element in file_content:
                    instance = ansibleInfoDTDLInstance()
                    instance.readInstanceFromJson(
                        element,
                        string_helper.get_folder(path))
                    self.instances.append(instance)
        except FileNotFoundError:
            print(f"Die Datei '{path}' wurde nicht gefunden.")
        except json.JSONDecodeError as e:
            print(f"Fehler beim Dekodieren der JSON-Datei: {e}")

    def savePlaybook(self, path: str, telegraf_config_path: str, dtdl_file_path: str, playbook_path:str, servicesPath: str):
        result = "---"
        for instance in self.instances:
            instance.generateCommandAsServiceFiles(servicesPath)
            result = string_helper.addLine(result, instance.getTasksString(telegraf_config_path, dtdl_file_path, playbook_path))
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(path, "w") as file:
            file.write(result)
            file.close()
    
    def saveInventoryFile(self, path: str):
        result = ""
        for instance in self.instances:
            result = string_helper.addLine(result, instance.getInventoryString(outputPath = path))
        with open(path, "w") as file:
            file.write(result)
            file.close()
    
    def save_telegraf_configs(self,
                              folder: str):
        for instance in self.instances:
            instance.save_telegraf_config(folder)