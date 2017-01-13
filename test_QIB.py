import unittest
import nose
import QIBPrototype
import argparse
import os
import ConfigParser
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
   - Write meta_data
   - Write data
   - write logging of subjects
        - New subject
        - New information
        - Nothing new
"""


class TestQIBDatatypeRetrieval(unittest.TestCase):

    filePath = "test_files/"
    configPath = "test_files/test_confs/"
    conf_file = 'test_files/test_confs/test.conf'

    def setup(self, conf_file):
        args = self.set_args({"connection": conf_file})
        project = QIBPrototype.make_connection(args)
        return project

    def test_main_connection(self):
        project = self.setup(conf_file)
        assert_not_equal(project, None)

    def test_wrong_connection(self):
        args = self.set_args({"connection": "test_files/test_confs/fail_conn.conf"})
        project = QIBPrototype.make_connection(args)
        self.assertEqual(project.__class__.__name__, "ConnectionError")

    def test_unfound_project(self):
        args = self.set_args({"connection":"test_files/test_confs/wrong_project.conf"})
        project = QIBPrototype.make_connection(args)
        self.assertEqual(project, None)

    def test_create_dir_structure(self):
        args = self.set_args({"params":"test_files/test_confs/test.conf"})
        path = QIBPrototype.create_dir(args)
        realPath = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        assert os.path.exists(str(realPath +"/"+ path))
        assert os.path.exists(str(realPath)+"/"+str(path+"/tags/"))
        assert os.path.exists(str(realPath+"/"+path + "/clinical/"))

    def test_write_params(self):
        args = self.set_args({"params":"test_files/test_confs/test.conf"})
        config = ConfigParser.ConfigParser()
        config.read(args.params)
        path = config.get('Study', 'STUDY_ID')
        QIBPrototype.write_params(path, args)

        with open(path + '/tags/tags.params', 'r') as tagParamFile:
            with open('test_files/tags.params', 'r') as testTagParamFile:
                assert tagParamFile.read() == testTagParamFile.read()

        with open(path + '/clinical/clinical.params', 'r') as clinicalParamFile:
            with open('test_files/clinical.params', 'r') as testClinicalParamFile:
                assert clinicalParamFile.read() == testClinicalParamFile.read()

        with open(path + '/study.params', 'r') as studyParamFile:
            with open('test_files/study.params', 'r') as testStudyParamFile:
                assert studyParamFile.read() == testStudyParamFile.read()

    def test_write_headers(self):
        args = self.set_args({"params":  conf_file})
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
        data_structure = [{'FreeSurfer1.0\\Gray matter\\Total gray matter volume': '156649.34', 'FreeSurfer1.0\\Gray matter\\Total cortical gray matter volume': '22164094.21', 'FreeSurfer1.0\\Gray matter\\Left hemisphere cortical gray matter volume': '1461661.59', 'FreeSurfer1.0\\Gray matter\\Subcortical gray matter volume': '1216493.64', 'FreeSurfer1.0\\White matter\\Right hemisphere cortical white matter volume': '16461.16', 'FreeSurfer1.0\\White matter\\Left hemisphere cortical white matter volume': '1164616.46', 'FreeSurfer1.0\\White matter\\Total cortical white matter volume': '1131646.19', 'FreeSurfer1.0\\Gray matter\\Right hemisphere cortical gray matter volume': '246161.16', 'subject': 'prj001_001', 'FreeSurfer1.0\\General results\\Brain Segmentation Volume Without Ventricles': '264616.46', 'FreeSurfer1.0\\General results\\Brain Segmentation Volume': '1131619.00'}]
        header_testList = ['subject', 'FreeSurfer1.0\\General results\\Brain Segmentation Volume', 'FreeSurfer1.0\\General results\\Brain Segmentation Volume Without Ventricles', 'FreeSurfer1.0\\Gray matter\\Left hemisphere cortical gray matter volume', 'FreeSurfer1.0\\Gray matter\\Right hemisphere cortical gray matter volume', 'FreeSurfer1.0\\Gray matter\\Total cortical gray matter volume', 'FreeSurfer1.0\\Gray matter\\Subcortical gray matter volume', 'FreeSurfer1.0\\Gray matter\\Total gray matter volume', 'FreeSurfer1.0\\White matter\\Left hemisphere cortical white matter volume', 'FreeSurfer1.0\\White matter\\Right hemisphere cortical white matter volume', 'FreeSurfer1.0\\White matter\\Total cortical white matter volume']
        tagFile = open("test.txt", "w")
        project = self.setup(conf_file)
        args = self.set_args({"params": conf_file})
        dataList, dataHeaderList = QIBPrototype.obtain_data(project, tagFile, args)
        tagFile.close()
        os.remove(tagFile.name)
        self.assertEqual(data_structure, dataList)
        self.assertEqual(dataHeaderList, header_testList)


    def test_no_QIB(self):
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        study_id = config.get('Study', 'STUDY_ID')
        tagFile = open(study_id+"/tags/tags.txt", "w")
        conf_no_QIB_file = "test_files/test_confs/no_QIB.conf"
        args = self.set_args({"params": conf_no_QIB_file})
        dataList = QIBPrototype.obtain_data(project, tagFile, args)
        self.assertEqual(dataList, [])

    def set_args(self, argsDict):
        parser = argparse.ArgumentParser()
        for k, v in argsDict:
            if "params" in k:
                parser.add_argument("--params")
            elif "tags" in k:
                parser.add_argument("--tags")
            elif "connection" in k:
                parser.add_argument("--connection")
        args = parser.parse_args()
        for k, v in argsDict:
            if "params" in k:
                args.params = v
            elif "tags" in k:
                args.tags = v
            elif "connection" in k:
                args.connection = v
        return args


if __name__ == '__main__':
    unittest.main()

