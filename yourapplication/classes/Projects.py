# Author:
# Date:
# Email:
# Description:
import json
import os
from datetime import datetime
from multiprocessing import active_children
from time import sleep

from . import Database


class Project:

    def __init__(self, **kwargs):
        self.project_id = None
        self.algorithm_id = kwargs.get('algorithm_id', None)
        self.project_name = kwargs.get('project_name', None)
        self.project_root_filepath = kwargs.get('project_root_filepath', None)
        self.algorithm_file_path = kwargs.get('algorithm_file_path', None)
        self.project_config_filename = kwargs.get('project_config_filename', None)
        self.algorithm_language = kwargs.get('algorithm_language', None)
        self.__PROJECT_DEBUG_SWITCH = True

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                        OBJECT MANAGEMENT                                #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def create_project(self, algorithm_file, language):
        """ Creates new QuantConnect Project from uploaded algorithm """


        # Execute command as a child process

        command = "lean project-create "
        command += json.dumps(self.project_root_filepath)
        command += " --language "
        command += language
        print("running " + command)

        os.system(command)

        # remove the template main.py
        if self.algorithm_language == 'python':
            main_file = 'main.py'
        else:
            main_file = 'Main.cs'
        os.system(f'rm {self.project_root_filepath}/{main_file}')

        # Save file in project directory
        print(
            f"==============SAVING ALGORITHM FILE {self.algorithm_file_path}========") if self.__PROJECT_DEBUG_SWITCH else 0
        algorithm_file.save(self.algorithm_file_path)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DB INTERACTIONS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def insert_project_query(self):
        """
        Inserts project
        """
        print(
            "==========INSERTING PROJECT INTO DB========") if self.__PROJECT_DEBUG_SWITCH else 0
        # Connect to the db
        db_conn = Database.Database()
        db_conn.connect_to_database()

        insert_data = (
                self.algorithm_id,
                self.project_name,
                self.project_root_filepath,
                self.project_config_filename,
                self.algorithm_file_path,
                self.algorithm_language
        )

        resultId = db_conn.insert_project_query(insert_data).lastrowid
        self.set_project_id(resultId)

    def select_project_query(self):
        """
        Gets project and stores data in member attributes
        """
        print(
                "==========SELECTING PROJECT FROM DB========") if self.__PROJECT_DEBUG_SWITCH else 0
        db_conn = Database.Database()
        db_conn.connect_to_database()
        query_params = (self.project_id,)

        project = db_conn.select_project_from_id_query(query_params).fetchall()

        # convert and store the query results to backtest attributes as
        # dictionary objects
        self.store_query_in_member_attributes(project[0])

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DATA CONVERTERS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def store_query_in_member_attributes(self, project):
        """
        Converts query result to object
        """
        print(
            '=================== STORING PROJECT DATA IN MEMBER ATTRIBUTES ================') if self.__PROJECT_DEBUG_SWITCH else 0
        self.set_project_id(project[0])
        self.set_algorithm_id(project[1])
        self.set_project_name(project[2])
        self.set_project_root_filepath(project[3])
        self.set_project_config_filename(project[4])
        self.set_algorithm_file_path(project[5])
        self.set_algorithm_language(project[6])

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   MEMBER ATTRIBUTE SETTERS                              #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def set_project_id(self, project_id):
        """ Sets the project id"""
        self.project_id = project_id

    def set_algorithm_id(self, algorithm_id):
        """ Sets the algo id"""
        self.project_name = algorithm_id

    def set_project_name(self, project_name):
        """ Sets the name"""
        self.project_name = project_name

    def set_project_root_filepath(self, project_root_filepath):
        """ Sets the file path"""
        self.project_name = project_root_filepath

    def set_algorithm_file_path(self, algorithm_file_path):
        self.algorithm_file_path = algorithm_file_path

    def set_algorithm_language(self, algorithm_language):
        self.algorithm_language = algorithm_language

    def set_project_config_filename(self, config_filepath):
        self.project_config_filename = config_filepath