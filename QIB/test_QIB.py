'''
Name: test_QIB
Function: Testing different functional aspects of QIBPrototype
Author: Jarno van Erp
Company: The Hvye

Functions that are tested:
   - Establishing connection
        - Good (test_main_connection)
        - Wrong (test_wrong_connection)
        - not finding project (test_unfound_project)
   - Create dir structure (test_create_dir_structure)
   - Write params (test_write_params)
   - Write header (test_write_headers)
   - Obtain data (test_obtain_data)
   - if no QIB is present (test_no_QIB)
   - Write meta_data (test_write_meta_data)
   - Write data (test_write_data)
   - write logging of subjects
        - New subject (test_write_logging_new_subject)
        - New information (test_write_logging_new_information)
        - Nothing new (test_write_logging_existing_information)
'''

import unittest
import QIBPrototype
from nose.tools import assert_not_equal
import argparse
import os
import sys
if sys.version_info.major == 3:
    import configparser as ConfigParser
elif sys.version_info.major == 2:
    import ConfigParser
import re 
import time
import shutil


class TestQIBDatatypeRetrieval(unittest.TestCase):

    file_path = "test_files/"
    configPath = "test_files/test_confs/"

    def setup(self, conf_file):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = conf_file
        project, connection = QIBPrototype.make_connection(args)
        return project, connection

    def empty_file(self, file_name):
        with open(file_name, 'w') as file_:
            file_.write("")
        with open(file_name, 'r') as file_:
            assert file_.read() == ""

    def test_main_connection(self):
        conf_file = 'test_files/test_confs/test.conf'
        project, connection = self.setup(conf_file)
        assert_not_equal(project, None)
        connection.disconnect()

    def test_wrong_connection(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = "test_files/test_confs/fail_conn.conf"
        project, connection = QIBPrototype.make_connection(args)
        print(project)
        self.assertEqual(project.__class__.__name__, "ConnectionError")

    def test_unfound_project(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--connection")
        args = parser.parse_args()        
        args.connection = "test_files/test_confs/wrong_project.conf"
        project, connection = QIBPrototype.make_connection(args)
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

        with open(path + '/tags/tags.params', 'r') as tag_param_file:
            with open('test_files/tags.params', 'r') as test_tag_param_file:
                self.assertEqual(tag_param_file.read(), test_tag_param_file.read())

        with open(path + '/clinical/clinical.params', 'r') as clinical_param_file:
            with open('test_files/clinical.params', 'r') as test_clinical_param_file:
                self.assertEqual(clinical_param_file.read(), test_clinical_param_file.read())

        with open(path + '/study.params', 'r') as study_param_file:
            with open('test_files/study.params', 'r') as test_study_param_file:
                self.assertEqual(study_param_file.read(), test_study_param_file.read())

    def test_write_headers(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.params = "test_files/test_confs/test.conf"
        config = ConfigParser.ConfigParser()
        config.read(args.params)
        path = config.get('Directory', 'path')
        study_id = config.get('Study', 'STUDY_ID')
        path = path+study_id
        tag_file, data_file, concept_file = QIBPrototype.write_headers(path, args)

        assert os.path.exists(os.path.realpath(tag_file.name))
        assert os.path.exists(os.path.realpath(concept_file.name))

        with open(tag_file.name, 'r') as tag_file_r:
            first_line = tag_file_r.readline()
            self.assertEqual(first_line, "\t".join(['Concept Path', 'Title', 'Description', 'Weight'])+"\n")

        with open(concept_file.name, 'r') as concept_file_r:
            first_line = concept_file_r.readline()
            self.assertEqual(first_line, "\t".join(['Filename', 'Category Code', 'Column Number', 'Data Label'])+"\n")

    def test_obtain_data(self):
        data_structure = [{'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\1 volume (mm^3)': u'6980.625', 'subject': u'PROOF001', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\entire (masked) image volume (mm^3)': u'2457600.0', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\1 volume (mm^3)': u'6980.625', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\0 volume (mm^3)': u'2450619.375', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\entire (masked) image volume (mm^3)': u'2457600.0'}]
        header_test_list = ['subject', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Left\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Left\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Left\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Left\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T0\\Right\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T1\\Right\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T3\\Right\\entire (masked) image volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\1 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\0 volume (mm^3)', 'MultiAtlas Appearance Model Segmentation with Volume Calculation 0.1\\Femoral Cartilage Volume T7\\Right\\entire (masked) image volume (mm^3)']
        conf_file = 'test_files/test_confs/test.conf'
        tag_file = open("test.txt", "w")
        project, connection = self.setup(conf_file)
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        data_list, data_header_list = QIBPrototype.obtain_data(project, tag_file, args)
        tag_file.close()
        os.remove(tag_file.name)
        self.assertEqual(data_structure, data_list)
        self.assertEqual(data_header_list, header_test_list)
        connection.disconnect()


    def test_no_QIB(self):
        config = ConfigParser.ConfigParser()
        config.read("test_files/test_confs/test.conf")
        study_id = config.get('Study', 'STUDY_ID')
        path = config.get('Directory', 'path')
        tagFile = open(path+study_id+"/tags/tags.txt", "w")
        conf_file = "test_files/test_confs/no_QIB.conf"
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        project, connection = self.setup(conf_file)
        data_list = QIBPrototype.obtain_data(project, tagFile, args)
        self.assertEqual(data_list, [])
        connection.disconnect()

    def test_write_meta_data(self):
        tag_file = open("test.txt", "w")
        conf_file = 'test_files/test_confs/test.conf'
        project, connection = self.setup(conf_file)
        parser = argparse.ArgumentParser()
        parser.add_argument("--params")
        args = parser.parse_args()
        args.tags = conf_file
        data_list, data_header_list = QIBPrototype.obtain_data(project, tag_file, args)
        tag_file.flush()
        with open("test.txt", "r") as tag_read_file:
            with open(self.file_path+ "tagstest.txt") as tag_test_file:
                self.assertEqual(tag_read_file.read(), tag_test_file.read())
        os.remove(tag_file.name)
        connection.disconnect()

    def test_write_data(self):
        data_file_name = "writedata.txt"
        concept_file_name = "writeconcepts.txt"
        data_list = [{"hoi":"hoi", "foo":"bar"}, {"foo":"bar"}, {"hoi":"hoi"}]
        data_header_list = ["hoi", "foo"]
        data_file = open(data_file_name, 'w')
        concept_file = open(concept_file_name, 'w')
        QIBPrototype.write_data(data_file, concept_file, data_list, data_header_list)

        with open(data_file_name, 'r') as data_final_file:
            with open(self.file_path+ "datatest.txt") as data_test_file:
                self.assertEqual(data_final_file.read(), data_test_file.read())

        with open(concept_file_name, 'r') as concept_final_file:
            with open(self.file_path+ "concepttest.txt", 'r') as  concept_test_file:
                self.assertEqual(concept_final_file.read(), concept_test_file.read())

    def test_write_logging_new_subject(self):
        rows = [["subject1\t","foo\n"], ["subject2\t", "bar\n"]]
        test_log = ["subject1\tfoo\n","subject2\tbar\n"]
        log_file = (self.file_path + "QIBSubjects.log")
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
        log_file = (self.file_path + "QIBSubjects.log")
        current_date = time.strftime("%Y-%m-%d %X")
        self.empty_file(log_file)
        QIBPrototype.check_subject(rows_new_subject)
        QIBPrototype.check_subject(rows_new_info)
        time_regex = ",[0-9]{3}:New info for Subject: "
        found = False
        with open(log_file, 'r') as open_log_file:
                for line in open_log_file:
                    if re.match(current_date+time_regex+test_log, line):
                        found = True
        assert found

    def test_write_logging_existing_information(self):
        rows_old_info = [["subject1\t","foo\n"]]
        test_log = "subject1\tfoo\n"
        log_file = (self.file_path + "QIBSubjects.log")
        current_date = time.strftime("%Y-%m-%d %X")
        QIBPrototype.check_subject(rows_old_info)
        time_regex = ",[0-9]{3}:New info for Subject: "
        not_found = True
        with open(log_file, 'r') as open_log_file:
                for line in open_log_file:
                    if re.match(current_date+time_regex+test_log, line):
                        not_found = False
        assert not_found

    @classmethod
    def tearDownClass(self):
        conf_file = 'test_files/test_confs/test.conf'
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        path = config.get('Directory', 'path')
        shutil.rmtree(path)


if __name__ == '__main__':
    unittest.main()

