import time
from datetime import datetime, timedelta

def get_start_time_and_date(): 
    start_time = time.time()
    current_date = datetime.now().strftime("%Y-%m-%d__%H-%M")
    return start_time, current_date

def format_delta_date(delta):
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_execution_time(start_time):
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_timedelta = timedelta(seconds=execution_time_seconds)
    execution_time_formatted =format_delta_date(execution_time_timedelta)
    return execution_time_formatted
