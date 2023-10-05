import string_helper
import json
import os

class telegraf_conf_entry:
    def get_as_string(self,
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        pass

    def read_from_json(self,
                        id: str,
                        jsonDef: json):
        pass

class telegraf_agent_settings(telegraf_conf_entry):
    interval : str
    round_interval : bool
    metric_batch_size : int
    metric_buffer_limit : int
    collection_jitter : str
    flush_interval : str
    flush_jitter : str
    precision : str
    hostname : str
    omit_hostname : bool
    id: str = ""

    def __init__(self,
                 interval : str = "1s",
                 round_interval : bool = True,
                 metric_batch_size : int = 1000,
                 metric_buffer_limit : int = 10000,
                 collection_jitter : str = "0s",
                 flush_interval : str = "10s",
                 flush_jitter : str = "0s",
                 precision : str = "0s",
                 hostname : str = "",
                 omit_hostname : bool = False) -> None:
        self.interval = interval
        self.round_interval = round_interval
        self.metric_batch_size = metric_batch_size
        self.metric_buffer_limit = metric_buffer_limit
        self.collection_jitter = collection_jitter
        self.flush_interval = flush_interval
        self.flush_jitter = flush_jitter
        self.precision = precision
        self.hostname = hostname
        self.omit_hostname = omit_hostname
        self.isInput = False
    
    def get_as_string(self,
                      name_override: str = "",
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[agent]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"interval = \"{self.interval}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + "round_interval = " + string_helper.get_bool_string(self.round_interval))
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"metric_batch_size = {self.metric_batch_size}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"metric_buffer_limit = {self.metric_buffer_limit}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"collection_jitter = \"{self.collection_jitter}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"flush_interval = \"{self.flush_interval}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"flush_jitter = \"{self.flush_jitter}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"precision = \"{self.precision}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"hostname = \"{self.hostname}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"omit_hostname = " + string_helper.get_bool_string(self.omit_hostname))

        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + f"[[outputs.file]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"files = [\"stdout\",\"/debug.txt\"]")

        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + f"[[inputs.exec]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"commands = [\"cat\"]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"name_override = \"stdin_input\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"data_format = \"influx\"")
       

        return result

class telegraf_socket_listener(telegraf_conf_entry):
    # def __init__(self,
    #              service_address: int,
    #              data_format: str,
    #              tls_allowed_certs: list([str])) -> None:
    #     self.service_address = service_address
    #     self.data_format = data_format
    #     self.tls_allowed_certs = tls_allowed_certs
    #     self.isInput= True

    def __init__(self,
                 id: str,
                 jsonDef: json) -> None:
        self.read_from_json(id, jsonDef)
        self.isInput= True

    def read_from_json(self,
                 id: str,
                       jsonDef: json):
        self.id = id
        if "@type" not in jsonDef:
            raise ValueError("'@type' not found.")
        if not (jsonDef["@type"] == "TelemetryRealizationSocketListener"):
            raise ValueError("'@type' must be 'TelemetryRealizationSocketListener'")
        if "serviceAddress" in jsonDef:
            self.service_address = jsonDef["serviceAddress"]
        else:
            raise ValueError("'TelemetryRealizationSocketListener' must have 'serviceAddress'")
        if "tlsAllowedCacerts" in jsonDef:
            self.tls_allowed_certs = jsonDef["tlsAllowedCacerts"]
        if "dataFormat" in jsonDef:
            self.data_format = jsonDef["dataFormat"]
        else:
            raise ValueError("'TelemetryRealizationSocketListener' must have 'dataFormat'")
    
    def get_as_string(self,
                      name_override: str = "",
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[[inputs.socket_listener]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"service_address  = \"{self.service_address}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"data_format = \"{self.data_format}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"name_override = {name_override}")
        # result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tagpass = [{name_override}]")
        return result
    
class telegraf_influx_sender(telegraf_conf_entry):
    # def __init__(self,
    #              urls: list([str]),
    #              database: str = string_helper.UNDEFINED_STRING,
    #              database_tag: str= string_helper.UNDEFINED_STRING,
    #              username: str = string_helper.UNDEFINED_STRING,
    #              password: str = string_helper.UNDEFINED_STRING,
    #              tls_ca: str = string_helper.UNDEFINED_STRING,
    #              tls_cert: str = string_helper.UNDEFINED_STRING,
    #              tls_key: str = string_helper.UNDEFINED_STRING) -> None:
    #     self.urls = urls
    #     self.database = database
    #     self.database_tag = database_tag
    #     self.username = username
    #     self.password = password
    #     self.tls_ca = tls_ca
    #     self.tls_cert = tls_cert
    #     self.tls_key = tls_key
    #     self.isInput= False
    
    def __init__(self,
                 id: str,
                 jsonDef: json) -> None:
        self.read_from_json(id, jsonDef)
        self.isInput= False

    def read_from_json(self,
                       id,
                       jsonDef: json):
        self.id = id
        if "@type" not in jsonDef:
            raise ValueError("'@type' not found.")
        if not (jsonDef["@type"] == "TelemetryRealizationInfluxStringWriter"):
            raise ValueError("'@type' must be 'TelemetryRealizationInfluxStringWriter'")
        if "urls" in jsonDef:
            self.urls = jsonDef["urls"]
        else:
            raise ValueError("'TelemetryRealizationInfluxStringWriter' must have 'urls'")
        if "database" in jsonDef:
            self.database = jsonDef["database"]
        else:
            self.database = string_helper.UNDEFINED_STRING
        if "databaseTag" in jsonDef:
            self.database_tag = jsonDef["databaseTag"]
        else:
            self.database_tag = string_helper.UNDEFINED_STRING
        if "username" in jsonDef:
            self.username = jsonDef["username"]
        else:
            self.username = string_helper.UNDEFINED_STRING
        if "password" in jsonDef:
            self.password = jsonDef["password"]
        else:
            self.password = string_helper.UNDEFINED_STRING
        if "tlsCa" in jsonDef:
            self.tls_ca = jsonDef["tlsCa"]
        else:
            self.tls_ca = string_helper.UNDEFINED_STRING
        if "tlsCert" in jsonDef:
            self.tls_cert = jsonDef["tlsCert"]
        else:
            self.tls_cert = string_helper.UNDEFINED_STRING
        if "tlsKey" in jsonDef:
            self.tls_key = jsonDef["tlsKey"]
        else:
            self.tls_key = string_helper.UNDEFINED_STRING

    def get_as_string(self,
                      tags: list([str]),
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[[outputs.influxdb]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"urls = {self.urls }")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"namepass  = {string_helper.get_tag_pass_string(tags)}")
        if self.database != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"database = \"{self.database}\"")
        if self.database_tag != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"database_tag = \"{self.database_tag}\"")
        if self.username != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"username = \"{self.username}\"")
        if self.password != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"password = \"{self.password}\"")
        if self.tls_ca != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_ca = \"{self.tls_ca}\"")
        if self.tls_cert != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_cert = \"{self.tls_cert}\"")
        if self.tls_key != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_key = \"{self.tls_key}\"")
        return result

class telegraf_socket_writer(telegraf_conf_entry):
    # def __init__(self,
    #              address: str,
    #              tls_ca: str = string_helper.UNDEFINED_STRING,
    #              tls_cert: str = string_helper.UNDEFINED_STRING,
    #              tls_key: str = string_helper.UNDEFINED_STRING) -> None:
    #     self.address = address
    #     self.tls_ca = tls_ca
    #     self.tls_cert = tls_cert
    #     self.tls_key = tls_key
    #     self.isInput= False
    
    def __init__(self,
                 id: str,
                 jsonDef: json) -> None:
        self.read_from_json(id, jsonDef)
        self.isInput= False

    def read_from_json(self,
                      id: str,
                        jsonDef: json):
        self.id = id
        if "@type" not in jsonDef:
            raise ValueError("'@type' not found.")
        if not (jsonDef["@type"] == "TelemetryRealizationSocketWriter"):
            raise ValueError("'@type' must be 'TelemetryRealizationSocketWriter'")
        if "address" in jsonDef:
            self.address = jsonDef["address"]
        else:
            raise ValueError("'TelemetryRealizationSocketWriter' must have 'address'")
        if "dataFormat" in jsonDef:
            self.data_format = jsonDef["dataFormat"]
        else:
            raise ValueError("'TelemetryRealizationSocketWriter' must have 'data_format'")
        if "tlsCa" in jsonDef:
            self.tls_ca = jsonDef["tlsCa"]
        else:
            self.tls_ca = string_helper.UNDEFINED_STRING
        if "tlsCert" in jsonDef:
            self.tls_cert = jsonDef["tlsCert"]
        else:
            self.tls_cert = string_helper.UNDEFINED_STRING
        if "tlsKey" in jsonDef:
            self.tls_key = jsonDef["tlsKey"]
        else:
            self.tls_key = string_helper.UNDEFINED_STRING

    def get_as_string(self,
                      tags: list([str]),
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[[outputs.socket_writer]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"address = \"{self.address}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"data_format = \"{self.data_format}\"")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"namepass = {string_helper.get_tag_pass_string(tags)}")
        if self.tls_ca != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_ca = \"{self.tls_ca}\"")
        if self.tls_cert != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_cert = \"{self.tls_cert}\"")
        if self.tls_key != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tls_key = \"{self.tls_key}\"")
        return result

class telegraf_mqtt_subscriber(telegraf_conf_entry):
    # def __init__(self,
    #              servers: list([str]),
    #              topics: list([str]),
    #              qos: int = 0,
    #              clientId: str = string_helper.UNDEFINED_STRING,
    #              username: str= string_helper.UNDEFINED_STRING,
    #              password: str= string_helper.UNDEFINED_STRING,
    #              dataFormat: str= string_helper.UNDEFINED_STRING) -> None:
    #     self.servers= servers
    #     self.topics= topics
    #     self.qos= qos
    #     self.clientId= clientId
    #     self.username= username
    #     self.password= password
    #     self.dataFormat= dataFormat
    #     self.isInput= True
    
    def __init__(self,
                 id: str,
                 jsonDef: json) -> None:
        self.read_from_json(id, jsonDef)
        self.isInput= True

    def read_from_json(self,
                       id,
                       jsonDef: json):
        self.id = id
        if "@type" in jsonDef:
            if not (jsonDef["@type"] == "TelemetryRealizationMQTTSubscriber"):
                raise ValueError("'@type' must be 'TelemetryRealizationMQTTSubscriber'")
        else:
            raise ValueError("'@type' not found.")
        if "servers" in jsonDef:
            self.servers = jsonDef["servers"]
        else:
            raise ValueError("'TelemetryRealizationMQTTSubscriber' must have 'servers'")
        if "topics" in jsonDef:
            self.topics = jsonDef["topics"]
        else:
            raise ValueError("'TelemetryRealizationMQTTSubscriber' must have 'topics'")
        if "qos" in jsonDef:
            self.qos = jsonDef["qos"]
        else:
            self.qos = 0
        if "clientId" in jsonDef:
            self.clientId = jsonDef["clientId"]
        else:
            self.clientId = string_helper.UNDEFINED_STRING
        if "username" in jsonDef:
            self.username = jsonDef["username"]
        else:
            self.username = string_helper.UNDEFINED_STRING
        if "password" in jsonDef:
            self.password = jsonDef["password"]
        else:
            self.password = string_helper.UNDEFINED_STRING
        if "dataFormat" in jsonDef:
            self.dataFormat = jsonDef["dataFormat"]
        else:
            raise ValueError("'TelemetryRealizationMQTTSubscriber' must have 'dataFormat'")

    def get_as_string(self,
                      name_override: str = "",
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[[inputs.mqtt_consumer]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"servers= {self.servers}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"topics = {self.topics}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"qos = {self.qos}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"name_override = {name_override}")
        #result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"tagpass = [{name_override}]")
        if self.clientId != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"clientId = \"{self.clientId}\"")
        if self.username != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"username = \"{self.username}\"")
        if self.password != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"password = \"{self.password}\"")
        if self.dataFormat != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"data_format = \"{self.dataFormat}\"")
        return result

class telegraf_mqtt_publisher(telegraf_conf_entry):
    # def __init__(self,
    #              servers: list([str]),
    #              topic: str,
    #              qos : int = 0,
    #              clientId: str = string_helper.UNDEFINED_STRING,
    #              username: str= string_helper.UNDEFINED_STRING,
    #              password: str= string_helper.UNDEFINED_STRING,
    #              dataFormat: str= string_helper.UNDEFINED_STRING) -> None:
    #     self.servers= servers
    #     self.topic= topic
    #     self.qos= qos
    #     self.clientId= clientId
    #     self.username= username
    #     self.password= password
    #     self.dataFormat= dataFormat
    #     self.isInput= False
    
    def __init__(self,
                 id: str,
                 jsonDef: json) -> None:
        self.read_from_json(id, jsonDef)
        self.isInput= False

    def read_from_json(self,
                       id: str,
                       jsonDef: json):
        self.id = id
        if "@type" in jsonDef:
            if not (jsonDef["@type"] == "TelemetryRealizationMQTTPublisher"):
                raise ValueError("'@type' must be 'TelemetryRealizationMQTTPublisher'")
        else:
            raise ValueError("'@type' not found.")
        if "servers" in jsonDef:
            self.servers = jsonDef["servers"]
        else:
            raise ValueError("'TelemetryRealizationSocketListener' must have 'servers'")
        if "topic" in jsonDef:
            self.topic = jsonDef["topic"]
        else:
            raise ValueError("'TelemetryRealizationSocketListener' must have 'topic'")
        if "qos" in jsonDef:
            self.qos = jsonDef["qos"]
        else:
            self.qos = 0
        if "clientId" in jsonDef:
            self.clientId = jsonDef["clientId"]
        else:
            self.clientId = string_helper.UNDEFINED_STRING
        if "username" in jsonDef:
            self.username = jsonDef["username"]
        else:
            self.username = string_helper.UNDEFINED_STRING
        if "password" in jsonDef:
            self.password = jsonDef["password"]
        else:
            self.password = string_helper.UNDEFINED_STRING
        if "dataFormat" in jsonDef:
            self.dataFormat = jsonDef["dataFormat"]
        else:
            raise ValueError("'TelemetryRealizationMQTTPublisher' must have 'dataFormat'")

    def get_as_string(self,
                      tags: list([str]),
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+0, indentationChar) + "[[outputs.mqtt]]")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"servers= {self.servers}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"topic = \'{self.topic}\'")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"qos= {self.qos}")
        result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"namepass = {string_helper.get_tag_pass_string(tags)}")
        if self.clientId != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"clientId = \"{self.clientId}\"")
        if self.username != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"username = \"{self.username}\"")
        if self.password != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"password = \"{self.password}\"")
        if self.dataFormat != string_helper.UNDEFINED_STRING:
            result = string_helper.addLine(result, string_helper.char_n_times(indentationCount+1, indentationChar) + f"data_format = \"{self.dataFormat}\"")
        return result

class telemetryConnector:
    def __init__(self,
                 id: str,
                 inputTelemetry: str,
                 outputTelemetries: list([str])):
        self.id = id
        self.inputTelemetry = inputTelemetry
        self.outputTelemetries = outputTelemetries

    def __init__(self, jsonDef: json):
        self.read_from_json(jsonDef)
    
    
    def read_from_json(self,
                       jsonDef: json):
        if "@type" not in jsonDef:
             raise ValueError("Any TelemetryConnector must have @type field.")
        if "id" in jsonDef:
            self.id = jsonDef["id"]
        else:
            raise ValueError("'TelemetryConnector' must have 'id'")
        if "inputTelemetry" in jsonDef:
            self.inputTelemetry = jsonDef["inputTelemetry"]
        else:
            raise ValueError("'TelemetryConnector' must have 'inputTelemetry'")
        if "outputTelemetries" in jsonDef:
            self.outputTelemetries = jsonDef["outputTelemetries"]
        else:
            raise ValueError("'TelemetryConnector' must have 'outputTelemetries'")

class telegraf_config:
    def __init__(self) -> None:
        self.config_entries: list([telegraf_conf_entry])= []
        self.config_entries.append(telegraf_agent_settings())
        self.telemetryConnectors: list([telemetryConnector]) = []
        pass
    
    def add_telemetry_realization(self,
                                  id: str,
                                 jsonDef: json):
         if "@type" not in jsonDef:
             raise ValueError("Any TelemetryRealization must have @type field.")
         typeString = jsonDef["@type"]
         print(f"add_telemetry_realization for type {typeString}")
         if typeString == "TelemetryRealizationMQTTSubscriber":
             self.config_entries.append(telegraf_mqtt_subscriber(id, jsonDef))
             return
         if typeString == "TelemetryRealizationMQTTPublisher":
             self.config_entries.append(telegraf_mqtt_publisher(id, jsonDef))
             return
         if typeString == "TelemetryRealizationSocketListener":
             self.config_entries.append(telegraf_socket_listener(id, jsonDef))
             return
         if typeString == "TelemetryRealizationInfluxStringWriter":
             self.config_entries.append(telegraf_influx_sender(id, jsonDef))
             return
         if typeString == "TelemetryRealizationSocketWriter":
             self.config_entries.append(telegraf_socket_writer(id, jsonDef))
             return
         raise ValueError(f"Type \"{typeString}\" not known for InstanceTelemetry.Realization")

    def add_telemetry_connector(self,
                                 jsonDef: json):
        self.telemetryConnectors.append(telemetryConnector(jsonDef))
    
    def get_connector_ids_input(self,
                                telemetryId: str):
        result : list[(str)]= []
        for telemetryConnector in self.telemetryConnectors:
            if telemetryId in telemetryConnector.inputTelemetries:
                result.append(telemetryConnector.id)
        return result
    
    def get_connector_ids_output(self,
                                telemetryId: str):
        result : list[(str)]= []
        for telemetryConnector in self.telemetryConnectors:
            if telemetryId in telemetryConnector.outputTelemetries:
                result.append(string_helper.cleanify_string(telemetryConnector.inputTelemetry))
        return result
    
    def get_as_string(self,
                      indentationChar: str = "  ",
                      indentationCount: int = 0):
        result = ""
        for config_entry in self.config_entries:
            print(f"config_entry.id={config_entry.id}")
            if config_entry.isInput:
                #name_override = self.get_connector_ids_input(config_entry.id)
                name_override : str = "\"" + string_helper.cleanify_string(config_entry.id) + "\""
                result = string_helper.addLine(result, config_entry.get_as_string(name_override, indentationChar, indentationCount))
            else:
                output_sources = self.get_connector_ids_output(config_entry.id)
                result = string_helper.addLine(result, config_entry.get_as_string(output_sources, indentationChar, indentationCount))
            
        return result
    
    def save_to_file(self, path: str):
        print(f"Telegraf_config file: {path}")
        result = self.get_as_string()
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(path, "w") as file:
            file.write(result)
            file.close()
