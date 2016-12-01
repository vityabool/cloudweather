#!/usr/bin/python

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import random
import time
import sys
import iothub_client
from iothub_client import *
from iothub_client_args import *

# HTTP options
# Because it can poll "after 9 seconds" polls will happen effectively
# at ~10 seconds.
# Note that for scalabilty, the default value of minimumPollingTime
# is 25 minutes. For more information, see:
# https://azure.microsoft.com/documentation/articles/iot-hub-devguide/#messaging
timeout = 241000
minimum_polling_time = 9

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubClient.send_event_async. 
# By default, messages do not expire.
message_timeout = 10000

receive_context = 0
avg_wind_speed = 10.0
message_count = 5
received_count = 0

# global counters
receive_callbacks = 0
send_callbacks = 0
blob_callbacks = 0

# chose HTTP, AMQP or MQTT as transport protocol
protocol = IoTHubTransportProvider.AMQP

# String containing Hostname, Device Id & Device Key in the format:
# "HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>"
connection_string = "HostName=temhub02.azure-devices.net;DeviceId=MyRSB;SharedAccessKey=TjkgV65nlX6wNBmlOusDWC0Q7QPSx6woDXCRGI2/6Kk="

msg_txt = "{\"deviceId\": \"myPythonDevice\",\"temperature\": %.2f}"

# some embedded platforms need certificate information

def gettem():
    temfile = open("/sys/bus/w1/devices/28-0315543db8ff/w1_slave")
    temtext = temfile.read()
    temfile.close()
    temdata = temtext.split("\n")[1].split(" ")[9]
    temperature = float(temdata[2:])
    temperature = temperature / 1000
    return temperature



def set_certificates(iotHubClient):
    from iothub_client_cert import certificates
    try:
        iotHubClient.set_option("TrustedCerts", certificates)
        print("set_option TrustedCerts successful")
    except IoTHubClientError as e:
        print("set_option TrustedCerts failed (%s)" % e)


def receive_message_callback(message, counter):
    global receive_callbacks
    buffer = message.get_bytearray()
    size = len(buffer)
    print("Received Message [%d]:" % counter)
    print("    Data: <<<%s>>> & Size=%d" % (buffer[:size].decode('utf-8'), size))
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print("    Properties: %s" % key_value_pair)
    counter += 1
    receive_callbacks += 1
    print("    Total calls received: %d" % receive_callbacks)
    return IoTHubMessageDispositionResult.ACCEPTED


def send_confirmation_callback(message, result, user_context):
    global send_callbacks
    print(
        "Confirmation[%d] received for message with result = %s" %
        (user_context, result))
    map_properties = message.properties()
    #print("    message_id: %s" % message.message_id)
    #print("    correlation_id: %s" % message.correlation_id)
    key_value_pair = map_properties.get_internals()
    #print("    Properties: %s" % key_value_pair)
    send_callbacks += 1
    #print("    Total calls confirmed: %d" % send_callbacks)


def blob_upload_confirmation_callback(result, user_context):
    global blob_callbacks
    print("Blob upload confirmation[%d] received for message with result = %s" % (user_context, result))
    blob_callbacks += 1
    print("    Total calls confirmed: %d" % blob_callbacks)


def iothub_client_init():
    # prepare iothub client
    iotHubClient = IoTHubClient(connection_string, protocol)
    if iotHubClient.protocol == IoTHubTransportProvider.HTTP:
        iotHubClient.set_option("timeout", timeout)
        iotHubClient.set_option("MinimumPollingTime", minimum_polling_time)
    # set the time until a message times out
    iotHubClient.set_option("messageTimeout", message_timeout)
    # some embedded platforms need certificate information
    # set_certificates(iotHubClient)
    # to enable MQTT logging set to 1
    if iotHubClient.protocol == IoTHubTransportProvider.MQTT:
        iotHubClient.set_option("logtrace", 0)
    iotHubClient.set_message_callback(
        receive_message_callback, receive_context)
    return iotHubClient


def print_last_message_time(iotHubClient):
    try:
        last_message = iotHubClient.get_last_message_receive_time()
        print("Last Message: %s" % time.asctime(time.localtime(last_message)))
        print("Actual time : %s" % time.asctime())
    except IoTHubClientError as e:
        if (e.args[0].result == IoTHubClientResult.INDEFINITE_TIME):
            print("No message received")
        else:
            print(e)


def iothub_client_sample_run():

    try:

        iotHubClient = iothub_client_init()

        while True:
            # send a few messages every minute
            print("IoTHubClient sending message")
            i = 1

            #for i in range(0, message_count):
            msg_txt_formatted = msg_txt % (
                  gettem())
            print "Message sent: ", msg_txt_formatted
            message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
            message.message_id = "message_%d" % i
            message.correlation_id = "correlation_%d" % i
            iotHubClient.send_event_async(message, send_confirmation_callback, i)
                
            print(
               "IoTHubClient.send_event_async accepted message [%d]"
               " for transmission to IoT Hub." %
                 i)

            print "------\nwaiting for message get received and sleep 15 sec.."
            time.sleep(15)

            # Wait for Commands or exit
            print("IoTHubClient waiting for commands, press Ctrl-C to exit")


    except IoTHubError as e:
        print("Unexpected error %s from IoTHub" % e)
        return
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped")

    print_last_message_time(iotHubClient)


def usage():
    print("Usage: iothub_client_sample.py -p <protocol> -c <connectionstring>")
    print("    protocol        : <amqp, http, mqtt>")
    print("    connectionstring: <HostName=<host_name>;DeviceId=<device_id>;SharedAccessKey=<device_key>>")


if __name__ == '__main__':

    try:
        (connection_string, protocol) = get_iothub_opt(sys.argv[1:], connection_string, protocol)
    except OptionError as o:
        print(o)
        usage()
        sys.exit(1)

    print("Start sendng temperature to IOT hub...")

    iothub_client_sample_run()
