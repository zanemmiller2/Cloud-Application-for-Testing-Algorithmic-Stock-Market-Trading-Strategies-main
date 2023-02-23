import os
import io
import yahoo_fin
from flask import render_template, send_file, request, redirect, Flask
from flask_navigation import Navigation

from yourapplication.classes.Backtests import Backtest
from yourapplication import app
from yourapplication.classes.Database import Database
from yourapplication.classes.Projects import Project
from yourapplication.classes.Plot import Plot
from yourapplication.plotting.plot import plot_equity
from yourapplication.classes.date_changer import Date_changer
from yourapplication.classes.YahooDataLoader import get_yahoo_data
from yourapplication.classes.Database import Database

###########################################################################
#                                                                         #
#                                                                         #
#                              Configs                                    #
#                                                                         #
#                                                                         #
###########################################################################

dirname = os.path.dirname(__file__)
PROJECTS_FOLDER = '/projects/'
BACKTEST_FOLDER = '/projects/backtests/'
PLOTS_FOLDER = '/plotting/plots/'

app.config['PROJECTS_FOLDER'] = PROJECTS_FOLDER
app.config['BACKTEST_FOLDER'] = BACKTEST_FOLDER
app.config['PLOTS_FOLDER'] = PLOTS_FOLDER
nav = Navigation()

nav.Bar('top', [
        nav.Item('Home', 'index'),
        nav.Item('Upload Project', 'load_project'),
        nav.Item('Run Backtest', 'run_project'),
        nav.Item('View Results', 'select_backtest'),
        nav.Item('Load Stock Data', 'load_stock_data')
])
__WEBAPP_DEBUG_SWITCH = True
nav.init_app(app)


###########################################################################
#                                                                         #
#                                                                         #
#                              Routes                                     #
#                                                                         #
#                                                                         #
###########################################################################
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/load-project')
def load_project():
    # lode a new project or algorithm screen
    return render_template('load_project.html',
                           languages={"python": "Python", "csharp": "C#"})


# Create a new project from algorithm
@app.route('/create-project', methods=['POST', 'GET'])
def create_project():
    # TODO IMPLEMENT INTERMEDIATE LOADING PAGE WHILE PROJECT LOADS
    db_conn = Database()
    db_conn.connect_to_database()

    if request.method == 'POST':

        #########################
        #                       #
        #   Collect form data   #
        #                       #
        #########################
        # list of algorithms loaded (should only be one)
        fileList = request.files.getlist("algorithm_file")
        algorithm_file = fileList[0]
        algorithm_id = request.form["algorithm_id"]
        # Name of the Project root
        project_directory_name = request.form['algorithm_project_name']
        # Project root path
        project_full_path = dirname \
                            + app.config['PROJECTS_FOLDER'] \
                            + project_directory_name
        algorithm_language = request.form['algorithm_language']

        if algorithm_language == 'python':
            algorithm_file_path = project_full_path + '/main.py'
        else:
            algorithm_file_path = project_full_path + '/Main.cs'

        ###############################
        #                             #
        #   Create project Object     #
        #                             #
        ###############################
        # Create project object
        new_project = Project(algorithm_id=algorithm_id,
                              project_name=project_directory_name,
                              project_root_filepath=project_full_path,
                              project_config_filename=project_full_path + '/config.json',
                              algorithm_file_path=algorithm_file_path,
                              algorithm_language=algorithm_language)

        # Count the number of projects that already exist in the
        # database with the given project name
        unique_project_count = check_unique_project_backtest(
                project_name=project_directory_name)

        # Create new project directory if the directory
        # and project name don't already exist
        if not os.path.exists(project_full_path) and unique_project_count == 0:
            # Create Lean Project with project_directory_name
            print("Creating Project") if __WEBAPP_DEBUG_SWITCH else 0
            new_project.create_project(algorithm_file, algorithm_language)

            # Upload project to DB
            print("Uploading Project") if __WEBAPP_DEBUG_SWITCH else 0
            new_project.insert_project_query()
            return redirect('/project-selector')

        else:
            print("Didnt create project -- Project already exists") \
                if __WEBAPP_DEBUG_SWITCH else 0

            # Refresh page with error message displayed
            return render_template('load_project.html',
                                   error="Enter a unique project name. "
                                         "A project with that name already "
                                         "exists!")


@app.route('/project-selector', methods=['GET', 'POST'])
def run_project():
    # TODO make intermediate loading page after running test to wait for results

    db_conn = Database()
    db_conn.connect_to_database()

    # Select project from list
    if request.method == 'GET':

        # Get project file paths stored in database to populate dropdown menu
        stored_project_names_ids = db_conn.select_project_names_ids_query()
        return render_template('select_project.html',
                               projects=stored_project_names_ids)

    # Run project
    elif request.method == 'POST':

        # gets selected project name from select_project.html
        project_id = request.form.get("projects")
        # build the --output path for running backtest
        backtest_name = request.form.get("backtest_destination")
        output_path = dirname + app.config[
            'BACKTEST_FOLDER'] + backtest_name

        # Get the file paths of selected project with matching project_id
        stored_project_file_paths = db_conn.select_project_paths_query(
            project_id)
        project_root_path = stored_project_file_paths[0][0]
        project_config_path = stored_project_file_paths[0][1]

        # Check if backtest with same name already exists in database
        unique_backtest_count = check_unique_project_backtest(
                backtest_name=backtest_name)
        if unique_backtest_count != 0:
            # backtest name already exists
            return render_template('select_project.html',
                                   error="Enter a unique backtest name. "
                                         "A backtest with that name already "
                                         "exists in the database")

        # Set config file
        tickers = request.form.get("tickers_to_load")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        configuration_parameters = {
                'ticker'    : tickers,
                'start_date': start_date,
                'end_date'  : end_date
        }

        if tickers != "":
            tickers = tickers.split(",")
            res = get_yahoo_data(tickers, start_date, end_date)
            errors = ["Data Loaded! Please see results for each ticker below: "]
            for ticker_res in res:
                errors.append(ticker_res)

        # Create backtest object
        backtest_object = Backtest(backtest_name=backtest_name,
                                   backtest_filename=output_path,
                                   project_id=project_id,
                                   algorithm_config_filepath=project_config_path,
                                   configuration_parameters=configuration_parameters)

        backtest_object.run_backtest(project_root_path)

        # Find the two json files in the output path
        for file in os.listdir(output_path):
            file_ext = os.path.splitext(file)
            if (file_ext[1] == '.json'
                    and 'data-monitor-report' not in file_ext[0]):

                # json backtest order events file
                if '-order-events' in file_ext[0]:
                    backtest_orders_file_path = os.path.join(output_path,
                                                             file)
                    backtest_object.set_backtest_order_events_filename(
                            backtest_orders_file_path)
                # regular backtest file
                else:
                    backtest_file_path = os.path.join(output_path,
                                                      file)
                    backtest_object.set_backtest_filename(backtest_file_path)

        backtest_object.insert_backtest_query()

        # Get backtest object back for plotting
        backtest_object.select_backtest_from_db()

        # Create plots
        filename = plot_equity(backtest_object)

        plot = Plot(backtest_id=backtest_object.backtest_id,
                    plot_type="plot_equity", plot_file_name=filename)
        plot.create_plot()

        print(
            "=====================+ GOING TO BACKTEST SELECTOR PAGE ====================") if __WEBAPP_DEBUG_SWITCH else 0

        return redirect('/select-backtest')


@app.route('/select-backtest', methods=['GET', 'POST'])
def select_backtest():
    """ Form to select the backtest for which the user wants to see results"""
    db_conn = Database()
    db_conn.connect_to_database()

    # Show dropdown of backtests to view
    if request.method == 'GET':
        # Get the backtest names and ids for populating the drop-down menu
        stored_backtest_names_ids = db_conn.select_backtest_names_ids_query()
        return render_template('select_backtest.html',
                               backtests=stored_backtest_names_ids)

    # Query DB And display results
    elif request.method == 'POST':
        # Gets the backtest_id from the user selection
        backtest_id = request.form.get("backtests")
        if backtest_id is None:
            print(
                    '==============NO BACKTEST ID SETTING TO DEFAULT 1=========') if __WEBAPP_DEBUG_SWITCH else 0
            backtest_id = 1

        # Get the backtest record from the db with the matching id
        backtest_pull = Backtest(backtest_id=backtest_id)
        backtest_pull.select_backtest_from_db()

        print('trade statistics', backtest_pull.formatted_trade_statistics)

        plot_ids = Plot(
            backtest_id=backtest_pull.backtest_id).select_plot_ids_from_backtest_id_query()

        return render_template('results_page.html',
                               orders_table=backtest_pull.formatted_orders_table,
                               total_orders_data=backtest_pull.formatted_total_orders_stats,
                               statistics_table=backtest_pull.make_trade_statistics_table(),
                               alpha_rt_stats_table=backtest_pull.formatted_alpha_runtime_statistics,
                               runtime_statistics=backtest_pull.formatted_runtime_statistics,
                               algorithm_configuration=backtest_pull.algorithm_configuration,
                               plot_ids=plot_ids)


@app.route('/plots/<plot_id>', methods=['GET'])
def get_plot(plot_id):
    """ Form to select the backtest for which the user wants to see results"""
    try:
        db_conn = Database()
        db_conn.connect_to_database()
    except Exception as e:
        # TODO HANDLE EXCEPTION IN APP SOMEHWERE
        print(f"database connection error in select_backtest {e}: {e.args}")

    # get plot_file
    plot = Plot(plot_id=plot_id)
    plot_file = plot.select_plot_from_plot_id()
    return send_file(
            io.BytesIO(plot_file),
            mimetype='image/png',
            as_attachment=False)


@app.route('/stock-data-load', methods=['GET', 'POST'])
def load_stock_data():

    # Display page
    if request.method == 'GET':
        return render_template('load_stock_data.html')

    # Load Data
    elif request.method == 'POST':
        # Load data if requested
        tickers = request.form.get("tickers_to_load")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        overwrite_data = request.form.get("overwrite_existing_data")
        data_to_alter_percent = request.form.get("data_to_alter_percent")
        max_alter_percent = request.form.get("max_alter_percent")
        
        data_to_alter_percent = 0 if data_to_alter_percent == "" else float(data_to_alter_percent)/100
        max_alter_percent = 0 if max_alter_percent == "" else float(max_alter_percent)/100
        

        print("=======DATE TYPE FROM PICKER ====== ")
        if overwrite_data is not None:
            overwrite_data = True

        if tickers != "":
            tickers = tickers.split(",")
            res = get_yahoo_data(tickers, start_date, end_date, overwrite_data, data_to_alter_percent, max_alter_percent)
            errors = ["Data Loaded! Please see results for each ticker below: "]
            for ticker_res in res:
                errors.append(ticker_res)
        else:
            errors = ["Please specify which stock you want load!"]
        
        return render_template('load_stock_data.html', errors=errors)



###########################################################################
#                                                                         #
#                                                                         #
#                              Helpers                                    #
#                                                                         #
#                                                                         #
###########################################################################
def check_unique_project_backtest(project_name=None, backtest_name=None):
    db_conn = Database()
    db_conn.connect_to_database()

    if backtest_name:
        unique_count = db_conn.count_unique_backtests_query(backtest_name)[0][
            0]
    else:
        unique_count = db_conn.count_unique_projects_query(project_name)[0][0]

    return unique_count
