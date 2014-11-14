#Necessary imports
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection

#Takes you to the home page
def home_page(request):
    return render_to_response("home_page.html")

#Takes you to a page where you can report a new aircraft accident
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

#This will route the user to the mapper page
#Depending on the get parameter, it will either display 100 most recent crash coordinates
#or 100 most fatal crash coordinates via the google maps API
def mapper(request):
    selection = request.GET.get("selection")
    selection = selection if selection else "most_recent" 
    if selection == "most_recent": 
        query = "SELECT latitude, longitude, eventDate FROM accident_report INNER JOIN tookPlaceAt ON accident_report.reportNumber = tookPlaceAt.reportNumber ORDER BY eventDate DESC LIMIT 100;"
    elif selection == "most_fatal":
        query = "SELECT latitude, longitude, totalFatalInjuries FROM accident_report INNER JOIN tookPlaceAt ON accident_report.reportNumber = tookPlaceAt.reportNumber ORDER BY totalFatalInjuries DESC LIMIT 100;"
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    results = [[r[0], r[1], str(r[2])] for r in results]
    print results
    context = {'coordinate_pairs': results, 'selection': selection}
    return render_to_response("mapper.html", context)

#Form where users can select the month/year to search for stats on
def time_search_form(request):
    c = {}
    c["years"] = ["Select Year"] + range(2002, 2015)
    c["months"] = ["Select Month","January","February","March","April","May","June","July","August","September","October","November","December"]
    return render_to_response("time_search_form.html", c)

#Given a month and year, returns aggregate accident statistics for that period of time
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

def airline_leaderboard(request):
    params = request.GET
    stat = params["stat"] if params.get("stat") else "totalFatalInjuries"
    if stat in ["totalFatalInjuries", "totalSeriousInjuries", "totalMinorInjuries"]:
        query = "SELECT SUM(%s) AS total, airlineName FROM (SELECT %s, airlineName FROM (SELECT %s, aircraftID FROM accident_report JOIN involves ON accident_report.reportNumber=involves.reportNumber) AS A JOIN (SELECT owns.aircraftID, carrier.airlineName FROM owns JOIN carrier ON owns.carrierID=carrier.carrierID) AS B ON A.aircraftID=B.aircraftID) AS C GROUP BY airlineName ORDER BY total DESC LIMIT 25"%(stat, stat, stat)
    else:
        query = "SELECT COUNT(*) AS total, airlineName FROM (SELECT totalSeriousInjuries, airlineName FROM (SELECT totalSeriousInjuries, aircraftID FROM accident_report JOIN involves ON accident_report.reportNumber=involves.reportNumber) AS A JOIN (SELECT owns.aircraftID, carrier.airlineName FROM owns JOIN carrier ON owns.carrierID=carrier.carrierID) AS B ON A.aircraftID=B.aircraftID) AS C GROUP BY airlineName ORDER BY total DESC LIMIT 25"
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    c = {"rows": results, "stat": stat}
    return render_to_response("airline_leaderboard.html", c)

#Takes user to a search form where they can view crash statistics by
#both State and/or Country
def location_search_form(request):
    cursor = connection.cursor()
    query = "SELECT DISTINCT state FROM location WHERE country='United States';"
    cursor.execute(query)
    states = sorted([r[0] for r in cursor.fetchall()])
    query = "SELECT DISTINCT country FROM location;"
    cursor.execute(query)
    countries = sorted([r[0] for r in cursor.fetchall()])
    c = {"states": states, "countries": countries}
    return render_to_response("location_search_form.html", c)

#Given a city or state, return the summary statistics for crashes in that area
def location_search_results(request):
    params = request.GET
    state, country = params["state"], params["country"]
    if state:
        query = "SELECT COUNT(*), SUM(totalFatalInjuries), SUM(totalMinorInjuries), SUM(totalSeriousInjuries), SUM(totalUninjured) FROM accident_report, location, occuredIn WHERE accident_report.reportNumber = occuredIn.reportNumber AND occuredIn.locationID = location.locationID AND location.state = '%s';"%(state)
    else:
        query = "SELECT COUNT(*), SUM(totalFatalInjuries), SUM(totalMinorInjuries), SUM(totalSeriousInjuries), SUM(totalUninjured) FROM accident_report, location, occuredIn WHERE accident_report.reportNumber = occuredIn.reportNumber AND occuredIn.locationID = location.locationID AND location.country = '%s';"%(country)
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()[0]
    c = {}
    c["total_accidents"] = results[0] if results[0] else 0
    c["total_fatal"] = results[1] if results[1] else 0
    c["total_serious"] = results[2] if results[2] else 0
    c["total_minor"] = results[3] if results[3] else 0
    c["total_uninjured"] = results[4] if results[4] else 0
    return render_to_response("location_search_results.html", c)

#Provides the user with details about the flight environments surrounding crashes
def flight_environment(request):
    #Some entries are listed as blank, some as unknown in the database
    #Combine these into one
    def combine_blank_and_unknown(results):
        #Convert from tuple to list
        results = [list(r) for r in results]
        #First, give the blank and unknown groups the same label
        for result in results:
            if result[0].lower()=="unknown" or result[0]=='':
                result[0] = "UNKNOWN"            
        #Get the sum for these two groups
        count = sum([r[1] for r in results if r[0] == "UNKNOWN"])        
        #Splice them out of the original result set
        results = [r for r in results if r[0] != "UNKNOWN" and r[0] != '']
        return results + [["UNKNOWN", count]]
    
    def get_detail_name(detail):
        if detail == "purposeOfFlight": return "Purpose Of Flight"
        elif detail == "weatherConditions": return "Weather Conditions"
        elif detail == "phaseOfFlight": return "Phase of Flight"
    
    context = {}
    cursor = connection.cursor()
    params = request.GET
    detail = "purposeOfFlight" if not params.get("detail") else params["detail"]
    query = "SELECT %s, COUNT(*) FROM flight_environment GROUP BY %s;"%(detail, detail)
    cursor.execute(query)
    results = cursor.fetchall()
    results = combine_blank_and_unknown(results)
    context["details"] = results
    context["detail_name"] = get_detail_name(detail)
    return render_to_response("flight_environment.html", context)












