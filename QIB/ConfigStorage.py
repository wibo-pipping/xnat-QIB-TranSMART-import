import QIB2TBatch


class ConfigStorage(object):

    def __init__(self, args):

        config_bool = False

        if args.__contains__("all") and args.__dict__["all"]:
            config_file = QIB2TBatch.check_file_existence(args.all, "all")
            self.set_connection_conf(config_file)
            self.set_params_conf(config_file)
            self.set_tags_conf(config_file)
            config_bool = True

        else:

            if args.__contains__("connection") and args.__dict__["connection"]:
                config_connection = QIB2TBatch.check_file_existence(args.connection, "connection")
                self.set_connection_conf(config_connection)
                config_bool = True

            if args.__contains__("params") and args.__dict__["params"]:
                config_params = QIB2TBatch.check_file_existence(args.params, "params")
                self.set_params_conf(config_params)
                config_bool = True

            if args.__contains__("tags") and args.__dict__["tags"]:
                config_tags = QIB2TBatch.check_file_existence(args.tags, "tags")
                self.set_tags_conf(config_tags)
                config_bool = True

        if not config_bool:
            self.error = "No configuration files given.\nExit"

    def set_connection_conf(self, config_connection):
            self.connection_name = config_connection.get('Connection', 'url')
            self.user = config_connection.get('Connection', 'user')
            self.pssw = config_connection.get('Connection', 'password')
            self.project_name = config_connection.get('Connection', 'project')
            self.patient_file = config_connection.get('Connection', 'patient_map_file')

    def set_params_conf(self, config_params):
            self.study_id = config_params.get('Study', "STUDY_ID")
            self.security_req = config_params.get('Study', 'SECURITY_REQUIRED')
            self.top_node = config_params.get('Study', 'TOP_NODE')
            self.base_path = config_params.get('Directory', 'path')

    def set_tags_conf(self, config_tags):
            self.tag_list = config_tags.get('Tags', 'Taglist').split(', ')