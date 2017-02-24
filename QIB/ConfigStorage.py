import QIB2TBatch


class ConfigStorage(object):


    def __init__(self, args):

        if "connection" in args:
            config_connection = QIB2TBatch.check_file_existence(args.connection, "connection")
            self.connection_name = config_connection.get('Connection', 'url')
            self.user = config_connection.get('Connection', 'user')
            self.pssw = config_connection.get('Connection', 'password')
            self.project_name = config_connection.get('Connection', 'project')
            self.patient_file = config_connection.get('Connection', 'patient_map_file')

        if "params" in args:
            config_params = QIB2TBatch.check_file_existence(args.params, "params")
            self.study_id = config_params.get('Study', "STUDY_ID")
            self.security_req = config_params.get('Study', 'SECURITY_REQUIRED')
            self.top_node = config_params.get('Study', 'TOP_NODE')
            self.base_path = config_params.get('Directory', 'path')

        if "tags" in args:
            config_tags = QIB2TBatch.check_file_existence(args.tags, "tags")
            self.tag_list = config_tags.get('Tags', 'Taglist').split(', ')
