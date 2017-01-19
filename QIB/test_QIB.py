import unittest
import nose
import QIBPrototype
import argparse
import os
import ConfigParser
import re 
import time
from nose.tools import assert_not_equal

"""
Functions that needs to be tested:
   - Establishing connection V
        - Good V
        - Wrong V
        - not finding project V
   - Create dir structure V
   - Write params V
   - Write header V
   - Obtain data V
   - if no QIB is present V
   - Write meta_data V
   - Write data V
   - write logging of subjects V
        - New subject V
        - New information V
        - Nothing new V
"""


class TestQIBDatatypeRetrieval(unittest.TestCase):

    filePath = "test_files/"
    configPath = "test_files/test_confs/"

    def setup(self, conf_file):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = conf_file
        project = QIBPrototype.make_connection(args)
        return project

    
    def empty_file(self, file_name):
        with open(file_name, 'w') as file_:
            file_.write("")
        with open(file_name, 'r') as file_:
            assert file_.read() == ""


    def test_main_connection(self):
        conf_file = 'test_files/test_confs/test.conf'
        project = self.setup(conf_file)
        assert_not_equal(project, None)

    def test_wrong_connection(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = "test_files/test_confs/fail_conn.conf"
        project = QIBPrototype.make_connection(args)
        print(project)
        self.assertEqual(project.__class__.__name__, "ConnectionError")

    def test_unfound_project(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = "test_files/test_confs/wrong_project.conf"
        project = QIBPrototype.make_connection(args)
        self.assertEqual(project, None)

    def test_create_dir_structure(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.params = "test_files/test_confs/test.conf"
        path = QIBPrototype.create_dir(args)
        assert os.path.exists(path)
        assert os.path.exists(path+"/tags/")
        assert os.path.exists(path + "/clinical/")

    def test_write_params(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.params = "test_files/test_confs/test.conf"
        config = ConfigParser.ConfigParser()
        config.read(args.params)
        base_path = config.get('Directory', 'path')
        study_path = config.get('Study', 'STUDY_ID')
        path = base_path+study_path
        QIBPrototype.write_params(path, args)

        with open(path + '/tags/tags.params', 'r') as tagParamFile:
            with open('test_files/tags.params', 'r') as testTagParamFile:
                assert tagParamFile.read() == testTagParamFile.read()

        with open(path + '/clinical/clinical.params', 'r') as clinicalParamFile:
            with open('test_files/clinical.params', 'r') as testClinicalParamFile:
                print(clinicalParamFile.read())
                print(testClinicalParamFile.read())
                assert clinicalParamFile.read() == testClinicalParamFile.read()

        with open(path + '/study.params', 'r') as studyParamFile:
            with open('test_files/study.params', 'r') as testStudyParamFile:
                assert studyParamFile.read() == testStudyParamFile.read()

    def test_write_headers(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.params = "test_files/test_confs/test.conf"
        config = ConfigParser.ConfigParser()
        config.read(args.params)
        path = config.get('Study', 'STUDY_ID')
        tagFile, dataFile, conceptFile = QIBPrototype.write_headers(path, args)

        assert os.path.exists(os.path.realpath(tagFile.name))
        assert os.path.exists(os.path.realpath(conceptFile.name))

        with open(tagFile.name, 'r') as tagFileR:
            firstLine = tagFileR.readline()
            self.assertEqual(firstLine, "\t".join(['Concept Path', 'Title', 'Description', 'Weight'])+"\n")

        with open(conceptFile.name, 'r') as conceptFileR:
            firstLine = conceptFileR.readline()
            self.assertEqual(firstLine, "\t".join(['Filename', 'Category Code', 'Column Number', 'Data Label'])+"\n")

    def test_obtain_data(self):
        data_structure = [{'FreeSurfer 1.0\\Gray matter\\Total gray matter volume': '156649.34', 'FreeSurfer 1.0\\Gray matter\\Total cortical gray matter volume': '22164094.21', 'FreeSurfer 1.0\\Gray matter\\Left hemisphere cortical gray matter volume': '1461661.59', 'FreeSurfer 1.0\\Gray matter\\Subcortical gray matter volume': '1216493.64', 'FreeSurfer 1.0\\White matter\\Right hemisphere cortical white matter volume': '16461.16', 'FreeSurfer 1.0\\White matter\\Left hemisphere cortical white matter volume': '1164616.46', 'FreeSurfer 1.0\\White matter\\Total cortical white matter volume': '1131646.19', 'FreeSurfer 1.0\\Gray matter\\Right hemisphere cortical gray matter volume': '246161.16', 'subject': 'prj001_001', 'FreeSurfer 1.0\\General results\\Brain Segmentation Volume Without Ventricles': '264616.46', 'FreeSurfer 1.0\\General results\\Brain Segmentation Volume': '1131619.00'}]
        header_testList = ['subject', 'FreeSurfer 1.0\\General results\\Brain Segmentation Volume', 'FreeSurfer 1.0\\General results\\Brain Segmentation Volume Without Ventricles', 'FreeSurfer 1.0\\Gray matter\\Left hemisphere cortical gray matter volume', 'FreeSurfer 1.0\\Gray matter\\Right hemisphere cortical gray matter volume', 'FreeSurfer 1.0\\Gray matter\\Total cortical gray matter volume', 'FreeSurfer 1.0\\Gray matter\\Subcortical gray matter volume', 'FreeSurfer 1.0\\Gray matter\\Total gray matter volume', 'FreeSurfer 1.0\\White matter\\Left hemisphere cortical white matter volume', 'FreeSurfer 1.0\\White matter\\Right hemisphere cortical white matter volume', 'FreeSurfer 1.0\\White matter\\Total cortical white matter volume']
        conf_file = 'test_files/test_confs/test.conf'
        tagFile = open("test.txt", "w")
        project = self.setup(conf_file)
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        dataList, dataHeaderList = QIBPrototype.obtain_data(project, tagFile, args)
        tagFile.close()
        os.remove(tagFile.name)
        self.assertEqual(data_structure, dataList)
        self.assertEqual(dataHeaderList, header_testList)


    def test_no_QIB(self):
        config = ConfigParser.ConfigParser()
        config.read("test_files/test_confs/test.conf")
        study_id = config.get('Study', 'STUDY_ID')
        tagFile = open(study_id+"/tags/tags.txt", "w")
        conf_file = "test_files/test_confs/no_QIB.conf"
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        project = self.setup(conf_file)
        dataList = QIBPrototype.obtain_data(project, tagFile, args)
        self.assertEqual(dataList, [])

    def test_write_meta_data(self):
        tagFile = open("test.txt", "w")
        conf_file = 'test_files/test_confs/test.conf'
        project = self.setup(conf_file)
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        dataList, dataHeaderList = QIBPrototype.obtain_data(project, tagFile, args)
        tagFile.flush()
        with open("test.txt", "r") as tagReadFile:       
            with open(self.filePath+"tagstest.txt") as tagTestFile:
                self.assertEqual(tagReadFile.read(), tagTestFile.read())
        os.remove(tagFile.name)

    def test_write_data(self):
        data_file_name = "writedata.txt"
        concept_file_name = "writeconcepts.txt"
        dataList = [{"hoi":"hoi", "foo":"bar"}, {"foo":"bar"}, {"hoi":"hoi"}]
        dataHeaderList = ["hoi", "foo"]
        dataFile = open(data_file_name, 'w')
        conceptFile = open(concept_file_name, 'w')
        QIBPrototype.write_data(dataFile, conceptFile, dataList, dataHeaderList)

        with open(data_file_name, 'r') as data_final_file:
            with open(self.filePath+"datatest.txt") as data_test_file:
                self.assertEqual(data_final_file.read(), data_test_file.read())

        with open(concept_file_name, 'r') as concept_final_file:
            with open(self.filePath+"concepttest.txt", 'r') as  concept_test_file:
                self.assertEqual(concept_final_file.read(), concept_test_file.read())

    def test_write_logging_new_subject(self):
        rows = [["subject1\t","foo\n"], ["subject2\t", "bar\n"]]
        test_log = ["subject1\tfoo\n","subject2\tbar\n"]
        log_file = (self.filePath+"QIBSubjects.log")
        self.empty_file(log_file)
        current_date = time.strftime("%Y-%m-%d %X")
        QIBPrototype.check_subject(rows)
        time_regex = ",[0-9]{3}:New subject: "        
        found1 = False
        found2 = False
        with open(log_file, 'r') as open_log_file:
                for line in open_log_file:
                    if re.match(current_date+time_regex+test_log[0], line):
                        found1 = True
                    if re.match(current_date+time_regex+test_log[1], line):
                        found2 = True
        assert found1
        assert found2

    def test_write_logging_new_information(self):
        rows_new_subject= [["subject3\t","foo\n"]]
        rows_new_info = [["subject3\t","foobar\n"]]
        test_log = "subject3\tfoobar\n"
        log_file = (self.filePath+"QIBSubjects.log")
        current_date = time.strftime("%Y-%m-%d %X")
        self.empty_file(log_file)
        QIBPrototype.check_subject(rows_new_subject)
        QIBPrototype.check_subject(rows_new_info)
        time_regex = ",[0-9]{3}:New info for Subject: "
        found = False
        with open(log_file, 'r') as open_log_file:
                print current_date+time_regex+test_log
                for line in open_log_file:
                    if re.match(current_date+time_regex+test_log, line):
                        found = True
        assert found

    def test_write_logging_existing_information(self):
        rows_old_info = [["subject1\t","foo\n"]]
        test_log = "subject1\tfoo\n"
        log_file = (self.filePath+"QIBSubjects.log")
        current_date = time.strftime("%Y-%m-%d %X")
        QIBPrototype.check_subject(rows_old_info)
        time_regex = ",[0-9]{3}:New info for Subject: "
        not_found = True
        with open(log_file, 'r') as open_log_file:
                for line in open_log_file:
                    if re.match(current_date+time_regex+test_log, line):
                        not_found = False
        assert not_found




if __name__ == '__main__':
    unittest.main()

