import re
from datetime import datetime


class Date_changer:

    def __init__(self, start_date, end_date, algo_path):
        self.start_date = start_date
        self.end_date = end_date
        self.algo_path = algo_path

    def change_date(self):
        reg = r'\([\s\S]*\)'

        start_date_obj = datetime.strptime(self.start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(self.end_date, '%Y-%m-%d').date()

        formatted_start_str = start_date_obj.strftime('(%Y, %-m, %-d)')
        formatted_end_str = end_date_obj.strftime('(%Y, %-m, %-d)')

        fr = open(self.algo_path, "r")
        # save contents of file to memory
        content = fr.readlines()
        # loop through content and search for lines to replace
        for i in range(len(content)):
            # replace start date
            if "self.SetStartDate" in content[i]:
                content[i] = re.sub(reg, formatted_start_str, content[i])
            # replace end date
            if "self.SetEndDate" in content[i]:
                content[i] = re.sub(reg, formatted_end_str, content[i])

        fr.close()
        # write updated start and end date to file
        fw = open(self.algo_path, "w")
        fw.writelines(content)
        fw.close()
