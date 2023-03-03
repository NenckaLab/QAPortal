import os
import re

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('agg')
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.dates as mdates
from django.views.generic import TemplateView, ListView
from .forms import DailyForm, HistoryForm
from .models import Graph
from decouple import config

class HomePageView(TemplateView):
    template_name = 'home.html'


class SearchResultsView(ListView):
    model = Graph
    template_name = 'search_results.html'


def home(request):
    context = {}
    return render(request, 'dashboard/home.html', context)


def daily(request):
    form = DailyForm(request.GET)
    context = {'form': form, "heading": "Enter Scanner, Coil, and Scan Date"}
    return render(request, 'dashboard/daily.html', context)    

def history(request):
    form = HistoryForm(request.GET or None)
    context = {'form': form, 'heading': 'Enter Scanner, Coil, Statistic, and Date Range'}
    return render(request, 'dashboard/history.html', context)

#Gets request from DailyForm and links to bxh-xcede-qa-tools' index.html file
def index(request):
    scandate = request.GET.get("scandate")
    scanner = request.GET.get("scanner")
    coil = request.GET.get("coil")
    if coil == "RM:32NovaHeadPR" and scanner == "MCWMR02":
        coil = "RM:32NovaHeadPR~"
    if datetime.strptime(scandate, '%Y-%m-%d') < datetime.strptime("2022-03-11",'%Y-%m-%d') and scanner == "MCWMR02":
        scanner = "MCWPREM"
    file_path = '/home/xnat/output/{}_{}/{}/fmriqa/'.format(scanner, coil, scandate)
    static_path = '/static/{}_{}/{}/fmriqa/'.format(scanner, coil, scandate)
    try:
        soup = BeautifulSoup(open(file_path + "index.html"), "html.parser")
        output = str(soup).split('\n')
        params = {}
        for row in output:
            if re.search('^<tr><td>', row):
                resoup = BeautifulSoup(row, 'html.parser').find_all('td')
                params[resoup[0].string] = resoup[1].string
        cbarmin = soup.find_all("td", {"class": "cbarmin"})
        cbarmax = soup.find_all("td", {"class": "cbarmax"})
        imgmin = soup.find_all("td", {"class": "imgmin"})
        imgmax = soup.find_all("td", {"class": "imgmax"})
        cmin = []
        cmax = []
        imin = []
        imax = []
        for e in cbarmin:
            cmin.append(e.string)
        for f in cbarmax:
            cmax.append(f.string)
        for g in imgmin:
            imin.append(g.string)
        for h in imgmax:
            imax.append(h.string)

        context = {'scanner': scanner, 'coil': coil, 'scandate': scandate, 'file_path': static_path, 'cmin': cmin,
                   'cmax': cmax, 'imgmin': imin, 'imgmax': imax, 'params': params}
    except:
        return render(request, 'dashboard/daily.html', {'form': DailyForm(request.GET), "heading":"Data not found Reenter Scanner, Coil, and Scan Date"})
    if os.path.exists(file_path+"index.html"):
        return render(request, 'dashboard/index.html', context)

def plot(request):
    template_name = 'plot.html'


# connects to DB and sends sql request
    try:
        conn = psycopg2.connect(f"dbname={config('PSQL_DB')} user={config('PSQL_USER')} password={config('PSQL_PASS')} port=5432")
    except Exception as e:
        return HttpResponse(e)
    try:
        coil = request.GET.get("coil")
        stats = request.GET.getlist("stat")
        scanner = request.GET.get("scanner")
        dates = request.GET.get("daterange").split(" - ")
        startDate = datetime.strptime(dates[0], "%m/%d/%Y").strftime("%Y-%m-%d")
        endDate = datetime.strptime(dates[1], "%m/%d/%Y").strftime("%Y-%m-%d")
    except Exception as e:
        return HttpResponse(e)
    if coil == "RM:32NovaHeadPR" and scanner == "MCWMR02":
        coil = "RM:32NovaHeadPR~"
    if datetime.strptime(startDate, '%Y-%m-%d') < datetime.strptime("2022-03-11",'%Y-%m-%d') and scanner == "MCWMR02":
        scanner = """MCWPREM, MCWMR02"""
    all = ['mean', 'SNR', 'SFNR', 'std', 'percentfluc', 'drift', 'driftfit','driftcmassx','driftcmassy','driftcmassz','dispcmassx','dispcmassy','dispcmassz', 'rdc', 'CMassX', 'CMassY', 'CMassZ', 'FWHMX', 'FWHMY', 'FWHMZ', 'MeanGhost', 'MeanBrightGhost']
    if stats[0]=='All':
        stats=all
    plotall={}
    count=0
    cur=conn.cursor()
    allstats={}
    plot_date={}
    sql_str = """SELECT scan_date FROM phantomqa WHERE scanner= '{}' AND coil='{}' AND scan_date BETWEEN '{}' AND '{}' ORDER BY scan_date DESC;""".format(
        scanner, coil,
        startDate, endDate)
    cur.execute(sql_str)
    dates = cur.fetchall()
    for d in dates:
        plot_date[count] = d
        count += 1
    count = 0
    try:
        for s in stats:
            #GRAPH NEEDS MULTIPLE LINES
            if s == "CMassX" or s == "CMassY" or s == "CMassZ" or s == "FWHMX" or s == "FWHMY" or s == "FWHMZ":
                minstat = f"min{s}"
                maxstat = f"max{s}"
                meanstat = f"mean{s}"
                sql_str = """SELECT {}, scan_date FROM phantomqa WHERE scanner='{}' AND coil='{}' AND scan_date BETWEEN '{}' AND '{}' ORDER BY scan_date DESC;""".format(minstat, scanner, coil, startDate, endDate)
                cur.execute(sql_str)
                minstat = cur.fetchall()
                sql_str = """SELECT {}, scan_date FROM phantomqa WHERE scanner='{}' AND coil='{}' AND scan_date BETWEEN '{}' AND '{}' ORDER BY scan_date DESC;""".format(maxstat, scanner, coil, startDate, endDate)
                cur.execute(sql_str)
                maxstat = cur.fetchall()
                sql_str = """SELECT {}, scan_date FROM phantomqa WHERE scanner='{}' AND coil='{}' AND scan_date BETWEEN '{}' AND '{}' ORDER BY scan_date DESC;""".format(meanstat, scanner, coil, startDate, endDate)
                cur.execute(sql_str)
                meanstat = cur.fetchall()
                plot_maxstat = {}
                plot_meanstat = {}
                plot_minstat = {}
                count = 0
                for h in maxstat:
                    plot_maxstat[count] = h[0]
                    count += 1
                count = 0
                for i in minstat:
                    plot_minstat[count] = i[0]
                    count += 1
                count = 0
                for k in meanstat:
                    plot_meanstat[count] = k[0]
                    count += 1
                count = 0
                plotall[s]= {'mean': plot_meanstat, 'min': plot_minstat, 'max': plot_maxstat}
            #GRAPH NEEDS SINGLE LINE
            else:
                sql_str = """SELECT {}, scan_date FROM phantomqa WHERE scanner='{}' AND coil='{}' AND scan_date BETWEEN '{}' AND '{}' ORDER BY scan_date DESC;""".format(s, scanner, coil, startDate, endDate)
                cur.execute(sql_str)
                allstats[s] = cur.fetchall()
                plotstat={}
                for a in allstats:
                    plotstat[count]=[]
                    for i in allstats[a]:
                        plotstat[count]=i[0]
                        count+=1
                    count=0
                plotall[s]= {s: plotstat}
            figure, plots = plt.subplots(len(stats), figsize=(12,(6*len(stats))), squeeze=False)
            i = 0 
            for p in plotall:
                if p == "CMassX" or p == "CMassY" or p == "CMassZ" or p == "FWHMX" or p == "FWHMY" or p == "FWHMZ":
                    plots[i,0].plot(plot_date.values(), plotall[p]['max'].values(), color="green", marker="o", linestyle="--", label=str(p)+" Max")
                    plots[i,0].plot(plot_date.values(), plotall[p]['min'].values(), color="red", marker="o", linestyle="--", label=str(p)+" Min")
                    plots[i,0].plot(plot_date.values(), plotall[p]['mean'].values(), color="blue", marker="o", linestyle="--", label=str(p)+" Mean")
                else:
                    plots[i,0].plot(plot_date.values(), plotall[p][p].values(), color="green", marker="o", linestyle="--", label=str(p))
                plots[i,0].set_xlabel('Date')
                plots[i,0].set_ylabel(str(p))
                plots[i,0].set_title("Longitudinal "+str(p))
                plots[i,0].legend()
                plots[i,0].grid()
                plots[i,0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                plots[i,0].legend()
                plots[i,0].xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))
                plt.xticks(rotation=45)
                i+=1
    except Exception as e:
#        return HttpResponse(traceback.format_exc())
        return render(request, 'dashboard/history.html', {'form': HistoryForm(request.GET), "heading":"Data not found Reenter Scanner, Coil, and Date Range"})
    figure.tight_layout()
    response = HttpResponse(content_type='image/png')
    canvas = FigureCanvasAgg(figure)
    canvas.print_png(response)
    return response

    
