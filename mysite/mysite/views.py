from django.shortcuts import render_to_response
from django.http import HttpResponse
from mapper.models import LatitudeLongitude
from django.db import connection

def hello(request):
    return render_to_response("home_page.html")

def reporter(request):
    c = {}
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT aircraftCategory FROM aircraft;")
    c["categories"] = sorted([r[0] for r in cursor.fetchall()])
    cursor.execute("SELECT DISTINCT make FROM aircraft;")
    c["makes"] = sorted([r[0] for r in cursor.fetchall()])    
    cursor.execute("SELECT DISTINCT model FROM aircraft;")
    c["models"] = sorted([r[0] for r in cursor.fetchall()])    
    cursor.execute("SELECT DISTINCT engineType FROM aircraft;")
    c["engine_types"] = sorted([r[0] for r in cursor.fetchall()])    
    return render_to_response("reporter.html", c)

def mapper(request):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM latitude_longitude LIMIT 500;")
    results = cursor.fetchall()
    context = {'coordinate_pairs': results}
    return render_to_response("mapper.html", context)

def time_search_form(request):
    c = {}
    c["years"] = ["Select Year"] + range(1990, 2015)
    c["months"] = ["Select Month","January","February","March","April","May","June","July","August","September","October","November","December"]
    return render_to_response("time_search_form.html", c)

def time_search_results(request):
    
    #Given a month as a string, return the appropriate integer mapping
    def month_to_int(m):
        if m == "January": return 1
        elif m == "February": return 2
        elif m == "March": return 3
        elif m == "April": return 4
        elif m == "May": return 5
        elif m == "June": return 6
        elif m == "July": return 7
        elif m == "August": return 8
        elif m == "September": return 9
        elif m == "October": return 10
        elif m == "November": return 11
        elif m == "December": return 12
        else: return -1
    
    params = request.GET
    print params
    month = int(month_to_int(params["month"]))
    year = int(params["year"]) if params["year"] != "Select Year" else -1
    cursor = connection.cursor()
    if year == -1 and month == -1:
        return time_search_form(request)
    elif year == -1 and month != -1:
        query = "SELECT COUNT(*), SUM(totalFatalInjuries), SUM(totalSeriousInjuries), SUM(totalMinorInjuries), SUM(totalUninjured) FROM accident_report WHERE MONTH(eventDate) = %i"%(month)
    elif month == -1 and year != -1:
        query = "SELECT COUNT(*), SUM(totalFatalInjuries), SUM(totalSeriousInjuries), SUM(totalMinorInjuries), SUM(totalUninjured) FROM accident_report WHERE YEAR(eventDate) = %i"%(year)       
    else:
        query = "SELECT COUNT(*), SUM(totalFatalInjuries), SUM(totalSeriousInjuries), SUM(totalMinorInjuries), SUM(totalUninjured) FROM accident_report WHERE MONTH(eventDate) = %i AND YEAR(eventDate) = %i"%(month, year)
    cursor.execute(query)
    results = cursor.fetchall()[0]
    c = {}
    c["total_accidents"] = results[0] if results[0] else 0
    c["total_fatal"] = results[1] if results[1] else 0
    c["total_serious"] = results[2] if results[2] else 0
    c["total_minor"] = results[3] if results[3] else 0
    c["total_uninjured"] = results[4] if results[4] else 0
    return render_to_response("time_search_results.html", c)







