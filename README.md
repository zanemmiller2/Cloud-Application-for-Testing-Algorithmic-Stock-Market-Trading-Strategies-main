# Cloud-based-Application-for-Testing-Algorithmic-Stock-Market-Trading-Strategies

# Run Instructions - Windows + Mac

1. Install docker and start
      https://docs.docker.com/get-docker/
      
2. Install Quantconnect 
      https://github.com/QuantConnect/Lean.git

3. Login into lean
      `lean login`
      
4. After cloning the repo You may need to delete the yourapplication/projects reinitialize the folder as a lean folder by executing `lean init` inside the yourapplication/projects folder
      1. `rm -rf yourapplication/projects`
      2. `mkdir yourapplication/projects`
      3. `cd yourapplication/projects`
      4. `lean init`

**5. Change db.db_credentials.py to reflect your login for your local db**

**6. cd to directory** `cd ~/path/to/Cloud-based-Application-for-Testing-Algorithmic-Stock-Market-Trading-Strategies`

**7. Source the database DDL:**
      - If not installed, install mariadb
   1. Login to your mysql
   2. execute: `source yourapplication/db/db_queries/capstone_db_DDL.sql`

**7. Create a python3.9 virtual env:**
   1. `sudo apt update`
   2. `sudo apt install python3.9`
   3. `sudo apt-get install python39-dev python39-venv`
   4. `python3.9 -m venv <venv-name>`
   5. `source <venv-name>/bin/activate`

   
**8. Build and run the project:**
   1. In order to run the application you need to export an environment variable that tells Flask where to find the application instance. **NOTE:** **If you are outside of the project directory make sure to provide the exact path to your application directory.** 
      1. Run in the command line: `export FLASK_APP=yourapplication`
      2. On Windows: `set FLASK_APP=yourapplication`
   2. Similarly, you can turn on the development features with the following command:
      1. `export FLASK_DEBUG=1`
      2. On Windows: `set FLASK_DEBUG=1`
   3. In order to install and run the application in editable mode you need to issue the following commands:
      1. `pip install -r requirements.txt`
      2. `flask run`


# Setting up and Running the project with an EC2 instance and AWS Mariadb RDS
**1. Set up an EC2 Instance** - [https://aws.amazon.com/ec2/](https://aws.amazon.com/ec2/)
**2. (Set up an RDS Database)** - [https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreateDBInstance.html](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreateDBInstance.html)
   1. You'll need to assign inbound rules to allow connections from your ec2 public and private ip addresses as well as any local hosts you want to allow access to. 
   2. Allow inbound permissions from your local ip and EC2 instance IPs (both public and private) [https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/authorizing-access-to-an-instance.html](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/authorizing-access-to-an-instance.html)
   
**3. You may need to install some software**
   1. `sudo yum update -y`
   2. Install docker - [https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/](https://www.cyberciti.biz/faq/how-to-install-docker-on-amazon-linux-2/)
      1. Ensure docker is running at this point
   3. Install git - `sudo yum install git -y`
   4. Install python3 - `sudo amazon-linux-extras install python3.8`
   5. create python3 virtual environment named 'env' - `python3.8 -m venv env` 
   6. Activate the virtual environment - `source env/bin/activate`
   7. Install python development pack - `sudo yum install python38-devel`
   8. upgrade pip - `pip install --upgrade pip` 
   9. Install lean cli -- `pip3 install lean`

**4. Clone the git repository**

**5. connect to your RDS** `mysql -h <rds endpoint> -u <username> -p`
   1. Credentials:
      1. endpoint = hostname
      2. user = AWS RD2 username
      3. passsword = AWS RD2 passsword 
   2. Source the capstone_db_DDL.sql file
   3. Exit mysql 


**6. create and checkout a new branch**

**7. edit the `db_credentials.py` to integrate with your RD2**
   - endpoint = hostname 
   - user = AWS RD2 username 
   - passsword = AWS RD2 passsword

**7. cd to the project root "Cloud-based-Application-for-Testing-Algorithmic-Stock-Market"**

**6. Install the project dependencies** - `pip3 install -r requirements.txt`

**7. Build and run the project:**
   1. In order to run the application you need to export an environment variable that tells Flask where to find the application instance. **NOTE:** **If you are outside of the project directory make sure to provide the exact path to your application directory.**
      1. `export FLASK_APP=yourapplication`
      2. `export FLASK_DEBUG=1`
      3. `flask run --host=0.0.0.0 --port=5000`
         1. You may need to add inbound rules to your EC2 project to access from your local browser
