import subprocess

class lgdb_tools(object):
    def __init__(self):
        self.java    = r'C:\Program Files (x86)\Java\jre7\bin\java.exe'
        #self.java    = r'C:\Program Files\Java\jre7\bin\java.exe'
        self.jarfile = r'accsoft-cals-extr-client-nodep.jar'
        self.j_api_str = '{} -jar {} -M DS -vs {} -t1 "{}" -t2 "{}" -N {} -F CSV -MD'

    def get_data(self, variable_name, t1, t2, filename):
        self.j_api_command = self.j_api_str.format(self.java, self.jarfile, variable_name, t1, t2, filename)
        self.p_call()
        return self.p.communicate()

    def p_call(self):
        self.p = subprocess.Popen(self.j_api_command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
