from datetime import datetime

def get_time(live, timestamp=None):
    if live:
        now = datetime.now()
        return now.year, now.month, now.day, now.hour, now.minute, now.second
    elif timestamp is not None:
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.year, dt_object.month, dt_object.day, dt_object.hour, dt_object.minute, dt_object.second
    else:
        raise ValueError("Deve ser fornecido um timestamp quando live=False.")

