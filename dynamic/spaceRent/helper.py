import datetime

def check_valid_datetime(now, start, end):
    if (start < now) or (end < now):
        return False

    if ((end-start).total_seconds() / 60 / 60 < 1):
        return False
    
    if not((start.minute == 0) or (start.minute == 30)) or not((end.minute == 0) or (end.minute == 30)):
        return False
    
    return True

def check_available(now, start, end, lag, list):
    return 1