import subprocess
import os
import sqlite3
import datetime
import sqlQueries
import sklearn
from sklearn import preprocessing, metrics, model_selection, linear_model, svm
import pyglmnet
import numpy
import math
import pickle
from functools import partial
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from fpdf import FPDF
from localUtil import getPrediction, scaler

# note, for convenience of writing many separate query functions
# the connection is defined globally
dbConn = sqlite3.connect("./LouData.db", detect_types=sqlite3.PARSE_DECLTYPES);
# dbConn.row_factory = sqlite3.Row
dbCursor = dbConn.cursor()
dbCursor.executescript(sqlQueries.E_speedConfigure_0)

def generatePDF(dayDeltas, inspectionTotals, failureTotals):
    pdf = FPDF()
    pdf.set_margins(25.4, 25.4, 25.4)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0,10,'City of Louisville Advanced Data Analytics',0,1,align='C')
    pdf.cell(0,10,'Predictive Health Inspections Report',0,1, align='C')
    pdf.ln()
    pdf.ln()

    pdf.set_font('Arial', 'I', 11)
    pdf.cell(0,12, 'note: 2-month statistics reflect values for all possible 2-month periods over the last 2 years', 0, 1)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0,6, 'Average number of inspections for a 2-month period: '+str(numpy.mean(inspectionTotals)), 0, 1)
    pdf.cell(0,6, 'Max number of inspections for a 2-month period: '+str(max(inspectionTotals)), 0, 1)
    pdf.cell(0,6, 'Min number of inspections for a 2-month period: '+str(min(inspectionTotals)), 0, 1)
    pdf.ln()

    pdf.cell(0,6, 'Average number of failures for a 2-month period: '+str(numpy.mean(failureTotals)), 0, 1)
    pdf.cell(0,6, 'Max number of failures for a 2-month period: '+str(max(failureTotals)), 0, 1)
    pdf.cell(0,6, 'Min number of failures for a 2-month period: '+str(min(failureTotals)), 0, 1)
    pdf.ln()

    pdf.cell(0,6, 'Avg day movement by failed inspections using smart schedule (2-month): '+str(numpy.mean(dayDeltas)), 0, 1)
    pdf.cell(0,6, 'Max number of average days moved: '+str(max(dayDeltas)), 0, 1)
    pdf.cell(0,6, 'Min number of average days moved: '+str(min(dayDeltas)), 0, 1)
    pdf.ln()

    dbCursor.execute(sqlQueries.G_inspectionAverageForYears_1.format(numYrs='1'))
    yearavg = dbCursor.fetchall()[0][0]
    dbCursor.execute(sqlQueries.G_inspectionAverageForYears_1.format(numYrs='2'))
    twoyearavg = dbCursor.fetchall()[0][0]
    dbCursor.execute(sqlQueries.G_inspectionAverageForYears_1.format(numYrs='4'))
    fouryearavg = dbCursor.fetchall()[0][0]
    dbCursor.execute(sqlQueries.G_inspectionAverageForYears_1.format(numYrs='8'))
    eightyearavg = dbCursor.fetchall()[0][0]

    pdf.cell(0,6, 'Average inspection power score for the last year: '   +str(yearavg), 0, 1)
    pdf.cell(0,6, 'Average inspection power score for the last 2 years: '+str(twoyearavg), 0, 1)
    pdf.cell(0,6, 'Average inspection power score for the last 4 years: '+str(fouryearavg), 0, 1)
    pdf.cell(0,6, 'Average inspection power score for the last 8 years: '+str(eightyearavg), 0, 1)
    pdf.ln()

    pdf.add_page()
    pdf.set_y(279/2-16/2)
    pdf.cell(0,16,'Bi-Monthly Analytics Evaluation Performance Charts',0,1, align='C')
    for img in os.listdir('./bimonthlyCharts'):
        pdf.ln()
        pdf.set_x(215.9/2-25.4*8/2)
        pdf.image(name='./bimonthlyCharts/'+img, type='png', w=25.4*8)
    pdf.output('./output/InspectionStatisticsReport.pdf', 'F')

def scatter_plot_with_correlation_line(x, y, color):
    #  adjusted from
    # http://stackoverflow.com/a/34571821/395857
    # x does not have to be ordered.

    # Scatter plot
    plt.scatter(x, y, facecolors='none', edgecolors=color, marker='o')

    # Add correlation line
    axes = plt.gca()
    m, b = numpy.polyfit(x, y, 1)
    X_plot = numpy.linspace(axes.get_xlim()[0],axes.get_xlim()[1],100)
    plt.plot(X_plot, m*X_plot + b, color+'-')


def savePerformanceGraph(inspectionInfo, startDate, endDate):

    # orderGenerator.sort(None, lambda x: x[1], False)
    # inspection info list elements should have the form below
    # (inspection_id, actualOrderPlacement, optimalOrderPlacement, bool didFail, actualScore, predictedOrderPlacement)

    # assemble lists for x and y values for actual, predicted, and optimal scheduling
    # the list is not rearranged in the process, so only need one y value array
    actualx = []
    predictedx = []
    optimalx = []
    powerScores = []
    for inspection in inspectionInfo:
        powerScores.append(inspection[-2])
        actualx.append(inspection[1])
        predictedx.append(inspection[-1])
        optimalx.append(inspection[2])


    # generate best fit lines
    actualm, actualb = numpy.polyfit(actualx, powerScores, 1)
    predictedm, predictedb = numpy.polyfit(predictedx, powerScores, 1)
    optimalm, optimalb = numpy.polyfit(optimalx, powerScores, 1)

    # draw and save the plot
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(8.5, 11, forward=True)
    plt.xlabel('Inspection Precedence')
    plt.ylabel('Power Score')
    plt.title('Model Performance for Period ' + startDate + ' - ' + endDate)
    redPatch = mpatches.Patch(color='red', label='Actual Schedule')
    bluePatch = mpatches.Patch(color='blue', label='Predictive Analytics Schedule')
    greenPatch = mpatches.Patch(color='green', label='Optimal Schedule')
    plt.legend(handles=[redPatch, bluePatch, greenPatch])

    scatter_plot_with_correlation_line(actualx, powerScores, 'r')
    scatter_plot_with_correlation_line(predictedx, powerScores, 'b')
    scatter_plot_with_correlation_line(optimalx, powerScores, 'g')
    # plt.show()

    # Save figure
    plt.savefig('./bimonthlyCharts/'+startDate+'_to_'+endDate+'_performance_assessment.png', dpi=300, format='png')


def getPeriodBounds(inspectionIds):
    dbCursor.execute(sqlQueries.G_modelPeriodBounds_1.format(rangeIds=str(tuple(inspectionIds))))
    data = dbCursor.fetchall()
    start = data[0][0].partition(" ")[0]
    end = data[0][1].partition(" ")[0]

    return start, end



def main():

    # delete any old performance graphs
    files = os.listdir('./bimonthlyCharts')
    for f in files:
        os.remove('./bimonthlyCharts/'+f)

    # initialize stat trackers
    dayDeltas = []
    inspectionTotals = []
    failureTotals = []

    # build stats for each 2-month period
    for month in range(2, 24):
        # get the raw data from the models
        dbCursor.execute(sqlQueries.G_monthOfModels_2.format(farBound=(month+2), closeBound=(month)))
        data = dbCursor.fetchall()
        ldata = []
        actualOrder = []
        optimalOrder = []
        predictedOrder = []

        # put datapoints in lists so they can be altered (for scaling)
        # also create a list of the inpsection ids in order for convenience
        for item in data:
            lItem = list(item)
            ldata.append(lItem)
            actualOrder.append(lItem[0])

        # delete unnecessary array
        del data

        # generate a list tuples of the form (inspection_id, predictedScore, actual score)
        orderGenerator = []
        for n in ldata:
            logit = numpy.array(n[1:-1])
            logit = scaler.transform(logit)
            pred = getPrediction(logit)
            # pred = numpy.mean(glmnet.predict(logit))
            orderGenerator.append([n[0], pred, n[-1]])

        # begin building list of date differentials
        dayDiffs = []

        # put list of inspections in optimalOrder
        orderGenerator.sort(None, lambda x: x[2], False)
        for item in orderGenerator:
            optimalOrder.append(item[0])
        i = 0
        for inspection in actualOrder:
            dayDiffItem = []
            dayDiffItem.append(inspection)
            dayDiffItem.append(i)
            i = i + 1
            index = optimalOrder.index(inspection)
            dayDiffItem.append(index)
            powerscore = orderGenerator[index][-1]
            if(powerscore < 85):
                dayDiffItem.append(True)
            else:
                dayDiffItem.append(False)
            dayDiffItem.append(powerscore)

            dayDiffs.append(dayDiffItem)


        # put list of inspections in predicted order
        orderGenerator.sort(None, lambda x: x[1], False)
        for item in orderGenerator:
            predictedOrder.append(item[0])

        # add the predictedOrder placement to the daydiff items
        i=0
        while i < len(dayDiffs):
            inspId = dayDiffs[i][0]
            dayDiffs[i].append(predictedOrder.index(inspId))
            i = i + 1

        # each daydiff now should have (inspection_id, actualOrderPlacement, optimalOrderPlacement, bool didFail, actualScore, predictedOrderPlacement)
        # now let's get stats on the failed inspections
        failsPredictDiff = []
        for diffItem in dayDiffs:
            if(diffItem[3]):
                failsPredictDiff.append(diffItem[-1]-diffItem[1])

        periodStart, periodEnd = getPeriodBounds(actualOrder)
        numInspections = len(predictedOrder)
        numFailures = len(failsPredictDiff)
        inspectionsperday = len(predictedOrder)/60.84
        dayssooner =float(numpy.mean(failsPredictDiff))/float(inspectionsperday)

        print 'period: ' + str(periodStart) + ' - ' + str(periodEnd)
        print 'inspections this two month period: ' + str(numInspections)
        print 'number of failures this period: ' + str(numFailures)
        print 'Average slots moved by failures: ' + str(numpy.mean(failsPredictDiff))
        print 'stddev slots moved by failures: ' + str(numpy.std(failsPredictDiff))
        print 'average day movement by failed inspections (estimate) : ' + str(dayssooner)
        print '\n'

        dayDeltas.append(dayssooner)
        inspectionTotals.append(numInspections)
        failureTotals.append(numFailures)
        savePerformanceGraph(dayDiffs, periodStart, periodEnd)


    print 'average days sooner for test: ' + str(numpy.mean(dayDeltas))
    print 'generating pdf report'
    generatePDF(dayDeltas, inspectionTotals, failureTotals)



    dbConn.commit()
    dbConn.close()

if __name__ == "__main__":
    main()

# pickle_file will be closed at this point, preventing your from accessing it any further
