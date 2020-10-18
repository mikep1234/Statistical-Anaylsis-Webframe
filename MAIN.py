from flask import Flask, render_template, request
import re, math
from flask_socketio import SocketIO

WEBAPP = Flask("localhost")

SENDER = SocketIO(WEBAPP)

@WEBAPP.route("/", methods = ["GET", "POST"])

def Help_Submission():

    return render_template("Home.html")

@SENDER.on('calculate_data')

def calculate_data(data):

    print(data)

    mean = 0

    median = 0

    mode = []

    q1, q3, IQR = 0, 0, 0

    range_val = 0

    stddev = 0

    ZVAL = re.split("[, ]", (data['Z_TO_CALC']))

    PERCENTILE = re.split("[, ]", (data['PERCENTILE_TO_CALC']))

    #Preparing the data to be analyzed

    data = re.split("[, ]", (data['data']))

    new_data = []

    for elem in data:

        try:

            new_data.append(float(elem))

        except:

            pass

    data = new_data

    data.sort()

    if len(data) > 0:

        # Below is for calculating the mean of the set

        for elem in data:

            try:

                    mean += float(elem)

            except:

                pass

        mean /= len(data)

        #Below is for calculating the median of the set

        holder_index = len(data)

        if len(data) <= 1:

            median = float(data[0])

        elif len(data) % 2 != 0 and len(data ) >= 2:

            median = float(data[int(holder_index / 2)])

        else:

            median = ((data[int(holder_index / 2)] + data[int(holder_index / 2) - 1]) / 2)

        #Below is for q1, q3, and IQR

        if len(data) >= 3:

            q1 = ((data[0] + data[int(holder_index / 2) - 1]) / 2)

            q3 = (data[int(holder_index / 2) + 1] + data[-1]) / 2

            IQR = q3 - q1

        #below is for mode

        mode_count = {}

        for elem in data:

            if elem not in mode_count:

                mode_count[elem] = 1

            else:

                mode_count[elem] = mode_count[elem] + 1

        mode = [float(max(mode_count, key=mode_count.get))]

        temp_mode = mode_count[float(max(mode_count, key=mode_count.get))]

        mode_sentinel = 0

        del mode_count[mode[0]]

        for elem in mode_count.items():

            if float(elem[1]) == temp_mode:

                mode.append(elem[0])

        mode_temp = []

        for elem in mode:

            mode_temp.append(str(elem))

        mode = ", ".join(mode_temp)

        #Below is for range

        if len(data) >= 2:

            range_val = float(data[-1]) - float(data[0])

        elif len(data) == 1:

            range_val = float(data[0])

        #Below is for Stddev

        if len(data) >= 2:

            stddev_subtotal = 0

            for elem in data:

                stddev_subtotal += ((float(elem) - mean) * (float(elem) - mean))

            stddev = math.sqrt(stddev_subtotal / len(data))

        if len(ZVAL) == 1:

            try:

                ZVAL = (float(ZVAL[0]) - mean) / stddev

            except:

                ZVAL = "DNE"

        else:

            ZVAL = "DNE"

        if len(PERCENTILE) == 1:

            try:

                float(PERCENTILE[0])

                if len(data) >= 2:

                    PERCENTILE = (float(PERCENTILE[0]) * 100.0) / len(data)

                else:

                    PERCENTILE = 100

            except:

                PERCENTILE = "DNE"

        else:

            PERCENTILE = "DNE"

        SENDER.emit('yield_data', {'PERCENTILE': str(PERCENTILE), 'Z-VAL': str(ZVAL), 'Q1': str(q1), 'Q3': str(q3), 'IQR': str(IQR), 'MEAN': str(mean), 'MEDIAN':  str(median), 'LENGTH': str(len(data)), 'MODE': mode, 'RANGE': str(range_val), 'STDDEV': str(stddev)}, room=request.sid)

SENDER.run(WEBAPP)