from picamera import PiCamera
import time
from fractions import Fraction
import datetime as dt
from datetime import datetime, time, timedelta
from dateutil import tz
from time import sleep
import json
import requests
import os
import sys
import Adafruit_DHT
import shutil

humidity, temperature = Adafruit_DHT.read_retry(11, 4)

# utc = datetime.strptime(str(sunrise_datetime), '%Y-%m-%d %H:%M:%S')
# utc = utc.replace(tzinfo=UTC_zone)
# pacific = utc.astimezone(PT_zone)
# print("Sunrise (Pacific) = ", str(pacific))

UTC_zone = tz.gettz('UTC')
PT_zone = tz.gettz('America/Los_Angeles')

def utc_to_local(utc):
    utc = utc.replace(tzinfo=UTC_zone)
    pacific = utc.astimezone(PT_zone)
    return pacific

def ss_calc(t1, utc_c, t2, ss1, ss2):
    if (t1 > t2):
        print("t1 greater than t2")
        return 0
    if (utc_c < t1 or utc_c > t2):
        print("utc not between t1 and t2")
        return 0
    print("ss_calc: t1 = ", str(t1), " t2 = ", str(t2))
    print("utc_c: ", str(utc_c))
    print("ss1 = ", ss1, "ss2 = ", ss2)
    diff = t2 - t1
    diffs = diff.total_seconds()
    print("diff (s) = ", diffs)
    diff2 = utc_c - t1
    diff2s = diff2.total_seconds()
    print("diff2 (s) = ", diff2s)
    ratio = diff2s / diffs
    print("ratio = ", ratio)
    ss_delta = int((ss2 - ss1) * ratio)
    print("ss_delta = ", ss_delta)
    final_ss = ss1 + ss_delta
    print("final_ss = ", final_ss)
    return final_ss

time_now_utc = datetime.utcnow()
print("time_now_utc (begin) = ", str(time_now_utc))

if (time_now_utc.hour < 12):
    time_now_utc = time_now_utc + timedelta(days=1)
    print("time_now_utc (shift 1 day) = ", str(time_now_utc))
else:
    print("time_now_utc (unshifted) = ", str(time_now_utc))
today_date = time_now_utc.date()
time_now = time_now_utc.time()
# time_str = time_now_utc.strftime("%Y%m%d%H%M_low")

now_local = dt.datetime.now()
print("\nTime Now (Pacific) = ", now_local.strftime("%Y-%m-%dT%H:%M:%S"))
time_str = now_local.strftime("%Y-%m-%d-%H:%M")

url = 'https://api.sunrise-sunset.org/json?lat=37.3064&lng=-121.98&formatted=0'
r = requests.get(url)

data = json.loads(r.content)

print("\nsunrise-sunset output: ", str(data))

sunrise  = data['results']['sunrise']
sunset   = data['results']['sunset']
ct_begin = data['results']['civil_twilight_begin']
ct_end   = data['results']['civil_twilight_end']
nt_begin = data['results']['nautical_twilight_begin']
nt_end   = data['results']['nautical_twilight_end']
at_begin = data['results']['astronomical_twilight_begin']
at_end   = data['results']['astronomical_twilight_end']

print("\ntime_now_utc = ", str(time_now_utc))
print("sunrise      = ", str(sunrise))
print("sunset       = ", str(sunset))
print("ct_begin     = ", str(ct_begin))
print("ct_end       = ", str(ct_end))

utc_now_datetime  = datetime.strptime(str(time_now_utc)[0:19], "%Y-%m-%d %H:%M:%S")
sunrise_datetime  = datetime.strptime(sunrise[0:19], "%Y-%m-%dT%H:%M:%S")
sunset_datetime   = datetime.strptime(sunset[0:19], "%Y-%m-%dT%H:%M:%S")
ct_begin_datetime = datetime.strptime(ct_begin[0:19], "%Y-%m-%dT%H:%M:%S")
ct_end_datetime   = datetime.strptime(ct_end[0:19], "%Y-%m-%dT%H:%M:%S")
nt_begin_datetime = datetime.strptime(nt_begin[0:19], "%Y-%m-%dT%H:%M:%S")
nt_end_datetime   = datetime.strptime(nt_end[0:19], "%Y-%m-%dT%H:%M:%S")
at_begin_datetime = datetime.strptime(at_begin[0:19], "%Y-%m-%dT%H:%M:%S")
at_end_datetime   = datetime.strptime(at_end[0:19], "%Y-%m-%dT%H:%M:%S")

print("utc_now_datetime.tzinfo = ", utc_now_datetime.tzinfo)
print("sunrise_datetime.tzinfo = ", sunrise_datetime.tzinfo)
print("at_begin_datetime.tzinfo = ", at_begin_datetime.tzinfo)

print("\ntime_now = ", str(time_now_utc))
print("at_begin = ", str(at_begin))
print("nt_begin = ", str(nt_begin))
print("ct_begin = ", str(ct_begin))

print("sunrise  = ", str(sunrise_datetime))
print("sunset   = ", str(sunset_datetime))

print("ct_end   = ", str(ct_end))
print("nt_end   = ", str(nt_end))
print("at_end   = ", str(at_end))

print("\nutc_now_datetime = ", str(utc_now_datetime))
print("at_begin_datetime = ", str(at_begin_datetime))
print("nt_begin_datetime = ", str(nt_begin_datetime))
print("ct_begin_datetime = ", str(ct_begin_datetime))
print("sunrise_datetime = ", str(sunrise_datetime))
print("sunset_datetime = ", str(sunset_datetime))
print("ct_end_datetime = ", str(ct_end_datetime))
print("nt_end_datetime = ", str(nt_end_datetime))
print("at_end_datetime = ", str(at_end_datetime))

# do some local times
# local time conversion

time_now_pacific = utc_to_local(time_now_utc)
print("Time now (Pacific) = ", time_now_pacific)
print("AT begin (Pacific) = ", utc_to_local(at_begin_datetime))
print("NT begin (Pacific) = ", utc_to_local(nt_begin_datetime))
print("CT begin (Pacific) = ", utc_to_local(ct_begin_datetime))
print("Sunrise (Pacific) = ", utc_to_local(sunrise_datetime))
print("Sunset (Pacific) = ", utc_to_local(sunset_datetime))
print("CT end (Pacific) = ", utc_to_local(ct_end_datetime))
print("NT end (Pacific) = ", utc_to_local(nt_end_datetime))
print("AT end (Pacific) = ", utc_to_local(at_end_datetime))

camera = PiCamera(framerate=Fraction(1,6))

night_ss = 6000000
at_ss    = 1000000
nt_ss    = 900000  # was 500000, to dark at end of ATE, at 700000, still too dark -> 900000
ct_ss    = 100000 # overexposed - was 10000 -> 100000
day_ss   = 100

# default to "daytime" shutter speed
camera.shutter_speed = 100

fin_ss = ss_calc(at_begin_datetime, datetime(2022, 2, 6, 13, 39), nt_begin_datetime, 10000, 100)

print("fin_ss = ", fin_ss)

if utc_now_datetime < at_begin_datetime:    # night
    print("before at_begin - night time")
    cam_txt = "NGT"
    camera.shutter_speed = night_ss
elif utc_now_datetime >= at_begin_datetime and utc_now_datetime < nt_begin_datetime:  # astronomical twilight
    print("astronomical twilight begin")
    cam_txt = "ATB"
    camera.shutter_speed = ss_calc(at_begin_datetime, utc_now_datetime, nt_begin_datetime, night_ss, at_ss)
elif utc_now_datetime >= nt_begin_datetime and utc_now_datetime < ct_begin_datetime:  # nautical twilight
    print("nautical twilight begin")
    cam_txt = "NTB"
    camera.shutter_speed = ss_calc(nt_begin_datetime, utc_now_datetime, ct_begin_datetime, at_ss, nt_ss)
elif utc_now_datetime >= ct_begin_datetime and utc_now_datetime < sunrise_datetime:  # civil twilight
    print("civil twilight begin")
    cam_txt = "CTB"
    camera.shutter_speed = ss_calc(ct_begin_datetime, utc_now_datetime, sunrise_datetime, nt_ss, ct_ss)
elif utc_now_datetime >= sunrise_datetime and utc_now_datetime < sunset_datetime: # daytime
    print("day time")
    cam_txt = "DAY"
    camera.shutter_speed = day_ss
elif utc_now_datetime >= sunset_datetime and utc_now_datetime < ct_end_datetime: # civil twilight
    print("civil twilight end")
    cam_txt = "CTE"
    camera.shutter_speed = ss_calc(sunset_datetime, utc_now_datetime, ct_end_datetime, day_ss, ct_ss)
elif utc_now_datetime >= ct_end_datetime and utc_now_datetime < nt_end_datetime: # nautical twilight
    print("nautical twilight end")
    cam_txt = "NTE"
    camera.shutter_speed = ss_calc(ct_end_datetime, utc_now_datetime, nt_end_datetime, ct_ss, nt_ss)
elif utc_now_datetime >= nt_end_datetime and utc_now_datetime < at_end_datetime: # astronomical twilight
    print("astronomical twilight end")
    cam_txt = "ATE"
    camera.shutter_speed = ss_calc(nt_end_datetime, utc_now_datetime, at_end_datetime, nt_ss, night_ss)
elif utc_now_datetime >= at_end_datetime: # night
    print("after at_end - night time")
    cam_txt = "NGT"
    camera.shutter_speed = night_ss
else:
    print("time not found")

print("=================================================")
print('Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity))
print('camera shutter speed = ', camera.shutter_speed)

cur_day_hour = time_now_pacific.hour
cur_day_date = str(time_now_pacific.month) + "-" + str(time_now_pacific.day) + "-" + str(time_now_pacific.year)
os.makedirs("/home/pi/allsky/" + cur_day_date, exist_ok=True)

# You can change these as needed. Six seconds (6000000)
# is the max for shutter speed and 800 is the max for ISO.
# camera.shutter_speed = 50000   # good for normal room light or twilight outdoors
# camera.shutter_speed = 500000  # good for darkened room
# camera.shutter_speed = 100   # good for outdoor daylight
camera.iso = 800
camera.resolution = (1024, 768)
camera.sensor_mode = 3

sleep(10)
camera.exposure_mode = 'off'

# track disk usage
total, used, free = shutil.disk_usage("/")
print("disk usage = ", total, used, free)
disk_used = used / total * 100
print("disk_used = ", disk_used)

tempf = (temperature * 1.8) + 32
title_text = cam_txt + dt.datetime.now().strftime(' %Y-%m-%d %H:%M:%S') \
        + ' Temp: {0:0.1f}F Hum: {1:0.1f}% DU: {2:0.1f}%'.format(tempf, humidity, disk_used)
camera.annotate_text = title_text
print('Title text = ', title_text)

outfile = "%s.jpg" % (time_str)
camera.capture(outfile)

camera.close()
