from datetime import datetime, date, timedelta
from typing import List

from exceptions.radiologoexception import InvalidDateFormatForEmissionException, InvalidDateForEmissionException
from ..models import Program, Slot


class ProgramService:
    def __init__(self):
        pass

    def create_program(self, authors, **extra_fields):
        p = Program(**extra_fields)
        p.save()
        p.authors.set(authors)
        return p

    def get_weekday_for_date(self, slot_set, enabled_days, date):
        try:
            emission_date_obj = datetime.strptime(date, "%Y%m%d")
        except ValueError:
            print("date is: " + date)
            raise InvalidDateFormatForEmissionException
        if slot_set.all().count() > 1:
            isoweekday = emission_date_obj.isoweekday()
            if isoweekday not in enabled_days:
                print("date is: " + date)
                raise InvalidDateForEmissionException

            weekday = slot_set.filter(weekday=Slot.iso_to_custom_format(isoweekday))[
                0].weekday
        else:
            weekday = ""
        return weekday

    def get_schedule(self):
        events = {"normal": [], "rerun": []}
        current_week_dates = []
        for i in range(1, 8):
            current_week_dates.append(
                (date.today() + timedelta(days=i - date.today().isoweekday())).isoformat()
            )
        for slot in Slot.objects.all():
            if slot.program.state == 'A':
                start = current_week_dates[slot.iso_weekday - 1] + " " + slot.time.strftime("%H:%M")
                end = current_week_dates[slot.iso_weekday - 1] + " " + slot.end_time()
                if slot.is_rerun:
                    events["rerun"].append(
                        {"name": slot.program.name + " - RE", "description": slot.program.description, "start": start,
                         "end": end})
                else:
                    events["normal"].append(
                        {"name": slot.program.name, "description": slot.program.description, "start": start,
                         "end": end})
        return events
    
    def get_current_slot(self):
        current_weekday = date.today().isoweekday()
        current_time = datetime.now().time()
        for slot in Slot.objects.all():
            if slot.program.state == 'A' \
            and slot.iso_weekday == current_weekday \
            and slot.time <= current_time \
            and slot.end_time_obj() >= current_time:
                start = slot.time.strftime("%H:%M")
                end = slot.end_time()
                if slot.is_rerun:
                    return {"name": slot.program.name + " - RE", "description": slot.program.description, "start": start,
                         "end": end, "type": "rerun"}
                else:
                    return {"name": slot.program.name, "description": slot.program.description, "start": start,
                         "end": end, "type": "normal"}
        return {}

