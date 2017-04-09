""""
Name: QIB2TBatch
Function: Library used by QIBconverter. This library contains all the functions needed to convert a QIB datatype to a
directory which can be uploaded to a TranSMART database.
Author: Jarno van Erp
Company: The Hyve

Requirements:
xnatpy      Downloadable here: https://bitbucket.org/bigr_erasmusmc/xnatpy

"""

import os
import sys
import logging
import xnat

if sys.version_info.major == 3:
    import configparser as ConfigParser
elif sys.version_info.major == 2:
    import ConfigParser


def make_connection(config):
    """
    Function: Create the connection to XNAT.
    Parameters:
        -config     ConfigStorage object    Object which holds the information stored in the configuration files.
    Returns: 
        -project    xnatpy object           Xnat connection to a specific project.
        -connection xnatpy object           Xnat wide connection.
    """

    try:
        connection = xnat.connect(config.connection_name, user=config.user, password=config.pssw)
        project = connection.projects[config.project_name]
        logging.info("Connection established.")
        return project, connection

    except KeyError:
        print("Project not found in XNAT.\nExit")
        logging.critical("Project not found in XNAT.")
        if __name__ == "__main__":
            sys.exit()
        else:
            return None, None

    except Exception as e:
        print(str(e) + "\nExit")
        if __name__ == "__main__":
            logging.critical(e.message)
            sys.exit()
        else:
            return e, None


def create_dir(config):
    """
    Function: Create the directory structure.
    Parameters:
        -config  ConfigStorage object    Object which holds the information stored in the configuration files.
    Returns: 
        -path    String                  Path to the directory where all the files will be saved.
    """

    path = config.base_path + config.study_id
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(path + "/tags/"):
        os.makedirs(path + "/tags/")
    if not os.path.exists(path + "/clinical/"):
        os.makedirs(path + "/clinical/")
    return path


def write_params(path, config):
    """
    Function: Uses the configuration files to write the .params files.
    Parameters:
        -path       String                  Path to the directory where all the files will be saved.
        -config     ConfigStorage object    Object which holds the information stored in the configuration files.
    """
    tag_param_file = open(path + '/tags/tags.params', 'w')
    tag_param_file.write("TAGS_FILE=tags.txt")
    study_param_file = open(path + '/study.params', 'w')
    study_param_file.write("STUDY_ID=" + config.study_id +
                           "\nSECURITY_REQUIRED=" + config.security_req +
                           "\nTOP_NODE=" + config.top_node)
    clinical_param_file = open(path + '/clinical/clinical.params', 'w')
    clinical_param_file.write("COLUMN_MAP_FILE=" + str(config.study_id) + "_columns.txt")
    tag_param_file.close()
    study_param_file.close()
    clinical_param_file.close()


def write_headers(path, config):
    """
    Function: Uses the configuration files to write the headers of the .txt files. 
    Parameters:
        -path           String                  Path to the directory where all the files will be saved.
        -config         ConfigStorage object    Object which holds the information stored in the configuration files.
    Returns:
        -tag_file        File                   tags.txt, used to upload the metadata into TranSMART.
        -data_file       File                   (STUDY_ID)_clinical.txt, used to upload the clinical data into TranSMART.
        -concept_file    File                   (STUDY_ID)_columns.txt, used to determine which values are in which columns for uploading to TranSMART.
    """

    data_file = open(path + '/clinical/' + config.study_id + '_clinical.txt', 'w')
    concept_file = open(path + '/clinical/' + config.study_id + '_columns.txt', 'w')
    tag_file = open(path + '/tags/tags.txt', 'w')
    # Hardcoded right now, because transmart does not need other headers. But this can be subject to change.
    concept_headers = ['Filename', 'Category Code', 'Column Number', 'Data Label']
    tag_headers = ['Concept Path', 'Title', 'Description', 'Weight']
    concept_file.write("\t".join(concept_headers) + '\n')
    tag_file.write("\t".join(tag_headers) + "\n")
    tag_file.flush()
    data_file.flush()
    concept_file.flush()
    return tag_file, data_file, concept_file


def obtain_data(project, tag_file, patient_map, config):
    """
    Function: Obtains all the QIB data from the XNAT project.
    Parameters: 
        -project             xnatpy object           Xnat connection to a specific project.
        -tag_file            File                    tags.txt, used to upload the metadata into TranSMART.
        -patient_map         Dictionary              Dictionary with the patient mapping with the XNAT identifier as key.
        -config              ConfigStorage object    Object which holds the information stored in the configuration files.
    Returns:
        -data_list           List                     List containing directories per subject, key = header, value = value.
        -data_header_list    List                     List containing all the headers.
    """
    concept_key_list = []
    data_header_list = []
    data_list = []
    tag_dict = {}
    for subject in project.subjects.values():
        data_row_dict = {}
        subject_obj = project.subjects[subject.label]
        for experiment in subject_obj.experiments.values():
            if "qib" in experiment.label.lower() and experiment.project == config.project_name:
                # Make number of returns and parameters less.
                data_header_list, data_row_dict, concept_key_list, tag_dict = retrieveQIB(subject_obj, experiment,
                                                                                          tag_file, data_row_dict,
                                                                                          subject, data_header_list,
                                                                                          concept_key_list, tag_dict,
                                                                                          patient_map, config)
        if len(data_row_dict) > 0:
            data_list.append(data_row_dict)

    if data_list == [{}] or data_list == []:
        logging.warning("No QIB datatypes found.")
        print("No QIB datatypes found.\nExit")
        if __name__ == "__main__":
            sys.exit()
        else:
            return data_list

    return data_list, data_header_list


def retrieveQIB(subject_obj, experiment, tag_file, data_row_dict, subject, data_header_list, concept_key_list, tag_dict,
                patient_map, config):
    """
    Function: Retrieve the biomarker information from the QIB datatype.
    
    Parameters:
        -subject_obj         Xnatpy.subject          Subject object derived from XNATpy
        -experiment          Xnatpy.experiment       Experiment object derived from XNATpy
        -tag_file            File                    File used to write the metadata tags to
        -data_row_dict       Dict                    Dictionary for storing the subject information, headers = key
        -subject             Subject                 Subject derived from XNATpy
        -data_header_list    List                    List used for storing all the headers
        -concept_key_list    List                    List used for storing the concept keys
        -tag_dict            Dictionary              Dictionary used to check if certain lines are already in the tagsfile.
        -patient_map         Dictionary              Dictionary with the patient mapping with the XNAT identifier as key.
        -config              ConfigStorage object    Object which holds the information stored in the configuration files.
    
    Returns:
        -data_header_list    List            List with the headers stored
        -data_row_dict       Dictionary      Dict containing all the QIB information of the subject
        -concept_key_list    List            List containing all the concept keys so far.
        -tag_dict            Dictionary      Dictionary used to check if certain lines are already in the tagsfile.
    """
    session = subject_obj.experiments[experiment.label]
    begin_concept_key, tag_dict = writeMetaData(session, tag_file, tag_dict, config)
    #data_row_dict['subject'] = patient_map[subject.label]
    data_row_dict['subject'] = subject.label
    if 'subject' not in data_header_list:
        data_header_list.append('subject')

    label_list = experiment.label.split('_')

    try:
        MRI_session = subject_obj.experiments["_".join(label_list[1:])]
        label = MRI_session._fields['laterality']
        timepoint = MRI_session._fields['timepoint']
    except KeyError:
        label = label_list[2]
        timepoint = label_list[3]

    for biomarker_category in session.biomarker_categories:
        results = session.biomarker_categories[biomarker_category]
        for biomarker in results.biomarkers:
            concept_value = results.biomarkers[biomarker].value
            concept_key = str(begin_concept_key) + '\\' + str(biomarker_category) + "\\" + label + "\\" + timepoint + \
                          "\\" + str(biomarker)
            data_row_dict[concept_key] = concept_value
            if concept_key not in data_header_list:
                data_header_list.append(concept_key)
                if __name__ == "__main__":
                    concept_key_list, tag_dict = writeOntologyTag(results, biomarker, concept_key, concept_key_list,
                                                                  tag_file, tag_dict, session)

    return data_header_list, data_row_dict, concept_key_list, tag_dict


def writeOntologyTag(results, biomarker, concept_key, concept_key_list, tag_file, tag_dict, session):
    """

    Parameters:
        -results            XNAT object         Parsed QIB XML object.
        -biomarker          XNAT object         biomarker from parsed XML.
        -concept_key        String              concept key for TranSMART
        -concept_key_list   List                List containing the already used concept keys.
        -tag_file           File                File for the metadata tags.
        -tag_dict           Dictionary          Dictionary used to check if certain lines are already in the tagsfile.
        -session            Xnatpy.session      Session object from xnatpy, used to retrieve the accession identifier.

    Returns:
        -concept_key_list     List          List containing the already used concept keys.
        -tag_dict             Dictionary    Dictionary used to check if certain lines are already in the tagsfile.

    """
    ontology_name = results.biomarkers[biomarker].ontology_name
    ontology_IRI = results.biomarkers[biomarker].ontology_iri
    if concept_key not in concept_key_list:
        ontology_name_row = [concept_key, "Ontology name", ontology_name]
        ontology_iri_row = [concept_key, "Ontology IRI", ontology_IRI]
        weight = "1"
        tag_file.write('\t'.join(ontology_name_row) + '\t' + weight + '\n')
        tag_file.write('\t'.join(ontology_iri_row) + '\t' + weight + '\n')
        if len(session.base_sessions.values()) >= 1:
            accession_identifier = session.base_sessions.values()[0].accession_identifier
            line = concept_key + "\taccession identifier\t" + str(accession_identifier) + "\t2\n"
            if line in tag_dict.keys():
                tag_dict[line] = True
                tag_file.write(line)
        concept_key_list.append(concept_key)
    return concept_key_list, tag_dict


def writeMetaData(session, tag_file, tag_dict, config):
    """
    Function: Write the metadata tags to the tag file.

    Parameters:
        -session       XNAT object              QIB datatype object in XNATpy
        -tag_file      File                     File for the metadata tags.
        -tag_dict      Dictionary               Dictionary used to check if certain lines are already in the tagsfile.
        -config        ConfigStorage object     Object which holds the information stored in the configuration files.

    Returns:
         -concept_key   String          concept key for TranSMART
         -tag_dict      Dictionary      Dictionary used to check if certain lines are already in the tagsfile.
    """

    analysis_tool = getattr(session, "analysis_tool")
    analysis_tool_version = getattr(session, "analysis_tool_version")
    if analysis_tool and analysis_tool_version:
        concept_key = str(analysis_tool + " " + analysis_tool_version)
    elif analysis_tool:
        concept_key = (analysis_tool)
    else:
        concept_key = "Generic Tool"
    i = len(config.tag_list)
    for tag in config.tag_list:
        try:
            info_tag = getattr(session, tag)
            if info_tag:
                line = concept_key + "\t" + tag.replace('_', ' ') + "\t" + str(info_tag) + "\t" + str(i) + "\n"
                i -= 1
                if line not in tag_dict.keys():
                    tag_dict[line] = True
                    tag_file.write(line)
        except AttributeError:
            logging.info(tag + " not found for " + str(concept_key))
    return concept_key, tag_dict


def write_data(data_file, concept_file, data_list, data_header_list):
    """
    Function: Writes the data from data_list to data_file.
    Parameters: 
        -data_file           File    (STUDY_ID)_clinical.txt, used to upload the clinical data into TranSMART.
        -concept_file        File    (STUDY_ID)_columns.txt, used to determine which values are in which columns for uploading to TranSMART.
        -data_list           List    List containing a directory per subject, key = header, value = value.
        -data_header_list    List    List containing all the headers.
    """
    data_file.write("\t".join(data_header_list) + '\n')
    column_list = []
    rows = []
    subject_written = False
    for line in data_list:
        row = []
        i = 0

        while i < len(data_header_list):
            row.append('\t')
            i += 1

        for header in data_header_list:
            if header in line.keys():
                info_piece = line[header]
                index = data_header_list.index(header)
                row[index] = info_piece + '\t'
                if header == "subject" and subject_written == False:
                    concept_file.write(str(os.path.basename(data_file.name)) + '\t' + str(header) + '\t' + str(
                        index + 1) + '\tSUBJ_ID\n')
                    subject_written = True
                    column_list.append(header)
                elif header not in column_list:
                    data_label = header.split("\\")[-1]
                    column_list.append(header)
                    concept_file.write(str(os.path.basename(data_file.name)) + '\t' + str(
                        "\\".join(header.split("\\")[:-1])) + '\t' + str(index + 1) + '\t' + str(data_label) + '\n')
        row[-1] = row[-1].replace('\t', '\n')
        data_file.write(''.join(row))
        rows.append(row)
    check_subject(rows)
    data_file.close()


def check_subject(rows):
    """
    Function: Checks in a log file if the subject is new or if there is information added or removed.

    Parameters:
        - rows   List    List containing lists with the retrieved QIB information of a subject.
    """

    #TODO Needs a way to read the header for each datapiece.

    if __name__ != "__main__":
        set_subject_logger(True)
        subject_logger = logging.getLogger("QIBSubjects")
    else:
        subject_logger = logging.getLogger("QIBSubjects")

    with open(subject_logger.handlers[0].baseFilename, "r") as log_file:
        log_data = log_file.read()

    written_to_file = []

    for row in rows:
        found_info = False
        found_subject = False
        if row[0] in log_data:
            found_subject = True
            if ''.join(row) in log_data:
                found_info = True

        if not found_subject and row not in written_to_file:
            subject_logger.info("New subject: " + ''.join(row))
            written_to_file.append(row)
        elif not found_info and row not in written_to_file:
            subject_logger.info("New info for Subject: " + ''.join(row))
            written_to_file.append(row)


def check_config_existence(file_, type):
    """
    Function: Checks if the configuration file exists and reads its content.
    Parameters:
        -file_      String      Path to configuration file.
        -type       String      Which type of configuration file.
    Returns:
        -config     Config      Parsed configuration file object.
    """

    try:
        file_test = open(file_, 'r')
        config = ConfigParser.SafeConfigParser()
        config.read(file_)
        file_test.close()
        return config

    except IOError:
        print("%s config file not found") % type
        logging.critical(type + " config file not found")
        sys.exit()


def configError(e):
    """
    Function: Error for when a variable is not found in a config file.

    Parameters:
        - e     Exception
    """
    logging.critical(e)
    if __name__ == "__main__":
        print(str(e) + "\nExit")
        sys.exit()


def set_subject_logger(test_bool):
    """
    Function: Creates a logger for subjects and new information.
    Parameter:
        -test_bool        Boolean   True = test
    Returns:
        -subject_logger   Logger    Logger to determine if a subject or its information is already parsed
    """
    logging.basicConfig(filename="QIBlog.log", format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
    subject_logger = logging.getLogger("QIBSubjects")
    subject_logger.setLevel(logging.INFO)

    if test_bool:
        ch = logging.FileHandler("test_files/QIBSubjects.log")
    else:
        ch = logging.FileHandler("QIBSubjects.log")

    ch.setLevel(logging.INFO)
    subform = logging.Formatter('%(asctime)s:%(message)s')
    ch.setFormatter(subform)
    subject_logger.addHandler(ch)
    return subject_logger


def get_patient_mapping(config):
    """
    Function: Parse the patient mapping file to a dictionary.
    Parameter:
        -config         ConfigStorage object     Object which holds the information stored in the configuration files.
    Returns:
        -patient_dict   Dictionary               Dictionary used to map the patient identifiers. Key is identifier from XNAT.
    """
    patient_dict = {}
    with open(config.patient_file, 'r') as patient_file:
        for line in patient_file:
            line_list = line.replace("\n","").split('\t')
            patient_dict[line_list[0]] = line_list[1]
    return patient_dict