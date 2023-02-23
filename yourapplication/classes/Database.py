# Author:
# Date:
# Email:
# Description:

from yourapplication.db.db_credentials import user, password, db_name, host
import pymysql as mariadb


class Database:

    def __init__(self):
        self.__host = host
        self.__user = user
        self.__password = password
        self.db_name = db_name
        self.db_connection = None
        self.__DB_DEBUG_SWITCH = True

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                              DB MANAGEMENT                              #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def connect_to_database(self):
        """
        connects to a database and returns a database objects
        """
        self.db_connection = mariadb.connect(host=self.__host,
                                             user=self.__user,
                                             password=self.__password,
                                             database=self.db_name)

    def execute_query(self, query=None, query_params=()):
        """
        executes a given SQL query on the given db connection and returns a Cursor object
        db_connection: a MySQLdb connection object created by connect_to_database()
        query: string containing SQL query
        returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
        You need to run .fetchall() or .fetchone() on that object to actually acccess the results.
        """

        if self.db_connection is None:
            print(
                    "No connection to the database found! Have you called connect_to_database() first?")
            return None

        if query is None or len(query.strip()) == 0:
            print("query is empty! Please pass a SQL query in query")
            return None

        print("Executing db query =========================")
        # print("Executing %s with %s" % (query, query_params))

        cursor = self.db_connection.cursor()

        cursor.execute(query, query_params)
        # this will actually commit any changes to the database. without this no
        # changes will be committed!
        self.db_connection.commit()
        return cursor

    def close_connection(self):
        self.db_connection.close()

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                              SELECTS                                    #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def select_project_names_ids_query(self):

        self.connect_to_database()

        """ Gets a listing of all the projects and their ids from db """
        print(
            "===============DB SELECTING PROJECT NAME AND ID========= ") if self.__DB_DEBUG_SWITCH else 0
        query = 'SELECT project_name, project_id FROM Projects'
        projects_names_ids = self.execute_query(query).fetchall()

        self.close_connection()
        return projects_names_ids

    def select_backtest_names_ids_query(self):
        """ Gets a listing of all the backtests and their ids from db """
        print(
                "===============DB SELECTING BACKTEST NAME AND ID========= ") if self.__DB_DEBUG_SWITCH else 0
        query = 'SELECT backtest_name, backtest_id FROM Backtests'
        backtest_names_ids = self.execute_query(query).fetchall()
        self.close_connection()
        return backtest_names_ids

    def select_project_paths_query(self, project_id):
        """
        Get the project's algorithm filepath and config filepath from the
        DB with the matching project_id
        """
        print(
                "===============DB SELECTING PROJECT PATHS========= ") if self.__DB_DEBUG_SWITCH else 0
        query = 'SELECT project_root_filepath, project_config_filename FROM Projects WHERE project_id = %s'
        query_params = (project_id,)
        project_paths = self.execute_query(query, query_params).fetchall()
        self.close_connection()
        return project_paths

    def select_backtest_from_id_query(self, backtest_id):
        """ Gets the backtest data from the db """
        print(
                "===============DB SELECTING BACKTEST RECORD WITH ID========= ") if self.__DB_DEBUG_SWITCH else 0
        select_query = 'SELECT * FROM Backtests WHERE backtest_id = %s'
        query_params = (backtest_id,)
        backtest_query = self.execute_query(select_query,
                                            query_params).fetchall()
        self.close_connection()
        return backtest_query

    def select_project_from_id_query(self, insert_data):
        """ SELECT project with matching id """
        print(
                "===============DB SELECTING PROJECT RECORD WITH ID========= ") if self.__DB_DEBUG_SWITCH else 0
        select_query = 'SELECT * FROM Projects WHERE project_id = %s'

        return self.execute_query(select_query, insert_data)

    def select_plot_ids_from_backtest_id_query(self, backtest_id):
        """ SELECT plot_ids with matching backtest_id """
        print(
                "===============DB SELECTING PLOT RECORD WITH ID========= ") if self.__DB_DEBUG_SWITCH else 0
        select_query = 'SELECT plot_id FROM Plots WHERE backtest_id = %s'

        return self.execute_query(select_query, backtest_id)

    def select_plot_file_from_plot_id_query(self, plot_id):
        """ SELECT plot with matching id """
        print(
                "===============DB SELECTING PLOT RECORD WITH ID========= ") if self.__DB_DEBUG_SWITCH else 0
        select_query = 'SELECT plot FROM Plots WHERE plot_id = %s'

        return self.execute_query(select_query, plot_id)

    def count_unique_projects_query(self, project_name):
        """ Counts number of db entries with the provided name """
        count_unique_projects_query = "SELECT COUNT(project_name) AS 'count' FROM Projects WHERE project_name=%s;"
        query_params = (project_name,)

        return self.execute_query(count_unique_projects_query,
                                  query_params).fetchall()

    def count_unique_backtests_query(self, backtest_name):
        """ Counts number of db entries with the provided name """
        count_unique_backtests_query = "SELECT COUNT(backtest_name) AS 'count' FROM Backtests WHERE backtest_name=%s;"
        query_params = (backtest_name,)

        return self.execute_query(count_unique_backtests_query,
                                  query_params).fetchall()

    def select_backtest_order_events(self, backtest_id):
        """ Selects the orders_events from """
        query = 'SELECT backtest_orders FROM Backtests WHERE backtest_id = %s;'
        query_params = (backtest_id,)
        return self.execute_query(query,
                                  query_params).fetchall()

    ###########################################################################
    #                                                                         #
    #                                                                         #
    #                              INSERTS                                    #
    #                                                                         #
    #                                                                         #
    ###########################################################################

    def insert_backtest_query(self, insert_data: tuple):
        """ Inserts a new backtest into the db """
        print(
                "===============DB INSERTING BACKTEST RECORD ========= ") if self.__DB_DEBUG_SWITCH else 0
        insert_query = 'INSERT INTO Backtests (' \
                       'project_id, configuration_id, ' \
                       'backtest_name, ' \
                       'backtest_order_events_file_path, ' \
                       'backtest_file_path, ' \
                       'algorithm_config_filepath,' \
                       'rolling_window, ' \
                       'total_performance, ' \
                       'alpha_runtime_statistics, ' \
                       'charts, ' \
                       'orders, ' \
                       'profit_loss, ' \
                       'statistics, ' \
                       'runtime_statistics, ' \
                       'algorithm_configuration, ' \
                       'backtest_orders) ' \
                       'VALUES (%s, %s, %s, %s, %s, %s, ' \
                       '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

        return self.execute_query(insert_query, insert_data)

    def insert_project_query(self, insert_data: tuple):
        """ Inserts a project into the db """
        print(
                "===============DB INSERTING PROJECT RECORD ========= ") if self.__DB_DEBUG_SWITCH else 0
        insert_query = 'INSERT INTO Projects (algorithm_id, project_name, project_root_filepath, project_config_filename, algorithm_file_path, algorithm_language) ' \
                       'VALUES (%s, %s, %s, %s, %s, %s)'

        return self.execute_query(insert_query, insert_data)

    def insert_plot_query(self, insert_data: tuple):
        """ Inserts a plot into the db """
        print(
                "===============DB INSERTING PLOT RECORD ========= ") if self.__DB_DEBUG_SWITCH else 0
        insert_query = 'INSERT INTO Plots (backtest_id, plot_type, plot) ' \
                       'VALUES (%s, %s, %s)'

        return self.execute_query(insert_query, insert_data)

    def insert_configurations_query(self, insert_data: tuple):
        """ Inserts new configuration entity into Configurations table """
        print(
                "===============DB INSERTING Configurations RECORD ========= ") if self.__DB_DEBUG_SWITCH else 0

        insert_query = 'INSERT INTO Configurations (configuration_parameters, configuration_file_path) VALUES (%s, %s);'
        return self.execute_query(insert_query, insert_data)

    def insert_project_configurations_query(self, insert_data: tuple):
        print(
                "===============DB INSERTING PROJECT_CONFIGURATIONS INTERSECTION RECORD ========= ") if self.__DB_DEBUG_SWITCH else 0

        insert_query = 'INSERT INTO Project_Configurations (configuration_id, project_id) VALUES (%s, %s);'

        self.execute_query(insert_query, insert_data)

