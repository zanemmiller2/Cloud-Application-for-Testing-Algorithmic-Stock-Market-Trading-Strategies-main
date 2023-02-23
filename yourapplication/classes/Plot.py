# Author:
# Date:
# Email:
# Description:
import json
import os
from datetime import datetime

from . import Database


class Plot:

    def __init__(self, **kwargs):
        self.plot_id = kwargs.get('plot_id', None)
        self.backtest_id = kwargs.get('backtest_id', None)
        self.plot_type = kwargs.get('plot_type', None)
        self.plot_file_name = kwargs.get('plot_file_name', None)
        self.plot_file = None
        self.__PLOT_DEBUG_SWITCH = kwargs.get('plot_debug_switch', None)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                        OBJECT MANAGEMENT                                #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def create_plot(self):
        """ Creates new QuantConnect Project from uploaded algorithm """

        if (self.backtest_id == None or self.plot_type == None or self.plot_file_name == None):
            print("Plot must have backtest_id, plot_type, and plot_file_path to be created")
            return
        
        print('=================== QUERYING RUN ================') if self.__PLOT_DEBUG_SWITCH else 0
        self.insert_plot_query()

        deletePlotCmd = 'rm ./yourapplication/plotting/plots/' + self.plot_file_name
        os.system(deletePlotCmd)

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DB INTERACTIONS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def insert_plot_query(self):
        """
        Inserts plot
        """
        print("==========INSERTING PLOT INTO DB========") if self.__PLOT_DEBUG_SWITCH else 0
        # Connect to the db
        try:
            db_conn = Database.Database()
            db_conn.connect_to_database()
        except Exception as e:
            # TODO HOW TO HANDLE THIS EXCEPTION
            print(f"database connection error in create_plot_query {e}: {e.args}")

        cwd = os.getcwd()
        file_path = cwd + "/yourapplication/plotting/plots/" + self.plot_file_name
        # read the binary data to vairable to upload to db
        with open(file_path, "rb") as fp:
            image_binary = fp.read()
        insert_data = (
                self.backtest_id,
                self.plot_type,
                image_binary,
        )

        resultId = db_conn.insert_plot_query(insert_data).lastrowid
        self.set_plot_id(resultId)

    def select_plot_ids_from_backtest_id_query(self):
        """
        Gets plots matching backtest_id returns them
        """
        print(
            "==========SELECTING PLOT IDs FROM DB========") if self.__PLOT_DEBUG_SWITCH else 0
        db_conn = Database.Database()
        db_conn.connect_to_database()
        query_params = (self.backtest_id,)

        plot_ids = db_conn.select_plot_ids_from_backtest_id_query(query_params).fetchall()

        print (plot_ids)

        # return plots
        return plot_ids

    def select_plot_from_plot_id(self):
        """
        Gets plots matching backtest_id returns them
        """
        print(
            "==========SELECTING PLOTs FROM DB========") if self.__PLOT_DEBUG_SWITCH else 0
        db_conn = Database.Database()
        db_conn.connect_to_database()
        query_params = (self.plot_id,)

        plot = db_conn.select_plot_file_from_plot_id_query(query_params).fetchall()
        plot_file = plot[0][0]

        # return plots
        return plot_file


    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                       DATA CONVERTERS                                   #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################


    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                   MEMBER ATTRIBUTE SETTERS                              #
    #                                                                         #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def set_plot_id(self, plot_id):
        """ Sets the plot id"""
        self.plot_id = plot_id

    def set_plot_file(self, plot_file):
        """ Sets the algo file"""
        self.plot_file = plot_file


