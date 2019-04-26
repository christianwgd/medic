# encoding: utf-8
import datetime

from django.template.defaultfilters import date


def getLocaleMonthNames():
    month_names = []
    for month_val in range(1, 13):
        month = datetime.datetime.strptime(str(month_val), "%m")
        month_names.append(date(month, 'b'))
    return month_names