# Author:
# Date:
# Email:
# Description:
from flask import Flask

app = Flask(__name__)

import yourapplication.webapp
from yourapplication.webapp import index, load_project, run_project, create_project, select_backtest
from yourapplication.webapp import *
