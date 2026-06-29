from datetime import datetime

class Get_time:
    def run(self,text:str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return current_time
get_time = Get_time()