#!/usr/bin/env python3

'''
Class to talk to a LeCrot WaveRunner Oscilloscope
'''

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from time import sleep

from vxi11 import Instrument


class WaveRunner(Instrument):  # pylint: disable=too-many-public-methods
    '''
    Class to talk to a LeCrot WaveRunner Oscilloscope
    '''

    def __init__(self, host='192.168.4.151'):
        '''
        Simple constructor not opnening communications
        :param host: the IP of the oscilloscope
        '''
        Instrument.__init__(self, host)
        self._is_configured = False
        self._sleep = 0.05
        self._saved_time_div = None

    def __timeout(self):
        '''
        Do not talk to fast to the scope
        '''
        sleep(self._sleep)

    def display_off(self):
        '''
        Turn display off
        '''
        self.write('DISP OFF')

    def display_on(self):
        '''
        Turn display on
        '''
        self.write('DISP ON')

    def prepare_data_taking(self):
        '''
        Set the data format of the scope to something readable
        '''
        self.write("CFMT DEF9,WORD,BIN")
        self.write("CHDR OFF")
        self.write('WFSU SP,0,NP,0,FP,0,SN,0')
        self.__timeout()

    def trigger_stop(self):
        '''
        Stop the trigger
        '''
        self.write('TRMD STOP')

    def trigger_normal(self):
        '''
        Start the trigger
        '''
        self.write('TRMD NORM')

    def beep(self):
        '''
        Make the oscilloscope beep
        '''
        self.write('BUZZ BEEP')

    def arm(self):
        '''
        Set to accumulate one trigger
        '''
        self.write('ARM')
        self.__timeout()

    def wait(self):
        '''
        Wait for trigger
        '''
        self.write('WAIT')

    @staticmethod
    def _get_arm_and_wait():
        '''
        Get string for exactly one trigger
        '''
        return 'ARM;WAIT'

    def arm_and_wait(self):
        '''
        Wait for exactly one trigger
        '''
        self.write(self._get_arm_and_wait())

    def get_trigger_mode(self):
        '''
        Get the current trigger mode
        '''
        return self.ask('TRMD?')

    def clear_sweeps(self):
        '''
        Clear all sweeps
        '''
        self.write('CLSW')

    def function_reset(self, function):
        '''
        Rest one function
        :param function: the function to reset
        '''
        self.write('%s:FRST' % function)

    def has_triggered(self):
        '''
        Check if osc has triggered
        '''
        return self.get_trigger_mode() == 'STOP\n'

    def get_time_div(self):
        '''
        return the time division
        '''
        return float(self.ask('TDIV?').strip())

    def set_time_div(self, timediv):
        '''
        set the time division
        :param timediv: the time division to set
        '''
        self.write('TDIV %s' % timediv)
        self.__timeout()

    def get_volt_div(self):
        '''
        Return the voltage division
        '''
        return float(self.ask('VDIV?').strip())

    def set_volt_div(self, channel, volt_div):
        '''
        Set the voltage division
        :param channel: the channel to change
        :param volt_div: the voltage division to use
        '''
        self.write('C%i:VDIV %s' % (channel, volt_div))
        self.__timeout()

    def get_trigger_level(self):
        '''
        Get the current trigger level
        '''
        return float(self.ask('TRLV?').strip())

    def set_trigger_level(self, trigger_level):
        '''
        Set the trigger level
        :param trigger_level: the level to use
        '''
        self.write('TRLV %s' % trigger_level)
        self.__timeout()

    def get_parameter(self, source, parameter):
        '''
        Get the paramteres from the scope for the given source
        :param source: the source to use
        :param parameter: the paramters to get
        '''
        if not parameter or not len(parameter):
            return None
        return self.ask('%s:PAVA? %s' % (source, parameter))

    def get_custom_parameter_settings(self, parameter_number):
        '''
        Gets a custom parameter
        :param parameter_number: the number of the custom parameter
        '''
        return self.ask('PACU? %i' % parameter_number).replace('\n', '')

    def get_statistics(self, parameter_number):
        '''
        Get the statistics for one parameter
        :param parameter_number: the parameter statistics to get
        '''
        if not parameter_number in range(1, 8):
            return None
        data = self.ask('PAST? CUST, P%i' % parameter_number).replace('\n', '').split(',')

        def try_convert(value):
            '''
            Make a float from an oscilloscope value
            :param value: the value to convert
            '''
            try:
                return float(value)
            except:  # pylint: disable=bare-except
                if value == 'UNDEF':
                    return None
                else:
                    return value

        return dict(zip(data[::2], [try_convert(value) for value in data[1::2]]))

    def wait_for_read(self):
        '''
        Wait for the oscilloscope to read in data
        '''
        try:
            self.read()
        except:  # pylint: disable=bare-except
            pass

    def configure(self):
        '''
        Prepare oscilloscope for data taking and save time div
        '''
        if not self._is_configured:
            self.prepare_data_taking()
            self._saved_time_div = self.get_time_div()
            self._is_configured = True

    def configure_for_skew(self):
        '''
        Prepare oscilloscope for data taking and save time div
        '''
        if not self._is_configured:
            self.prepare_data_taking()
            self.write('PACU 1,SKEW,C1,POS,50 PCT,C2,POS,50 PCT,500E-3 DIV,500E-3 DIV')
            self.write('PACU 2,SKEW,C1,POS,50 PCT,C3,POS,50 PCT,500E-3 DIV,500E-3 DIV')
            self.write('PACU 3,SKEW,C1,POS,50 PCT,C4,POS,50 PCT,500E-3 DIV,500E-3 DIV')
            self._saved_time_div = self.get_time_div()
            self._is_configured = True
        
            
    def __enter__(self):
        self.configure()
        return self

    def unconfigure(self):
        '''
        Undo changes to the oscilloscope
        '''
        if self._is_configured:
            self.set_time_div(self._saved_time_div)
            self._is_configured = False

    def __exit__(self, *_):
        self.unconfigure()


from pysnmp.hlapi import *
from time import sleep
import sys

from influxdb import InfluxDBClient
host = "localhost"
port = 8086
user = "root"
password = "root"
dbname = "oszi"


def main():  # pylint: disable=too-many-branches
    '''
    Read oscilloscope from console
    '''
    import matplotlib.pyplot as plt

    parser = ArgumentParser(description='Script to talk to the oscilloscope',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', '--ip', default='192.168.4.151',
                        help='IP address of the oscilloscope to connect to')

    args = parser.parse_args()

    # connect to DB
    client = InfluxDBClient(host, port, user, password, dbname)

    with WaveRunner(args.ip) as osc:
        #print(osc.ask('*IDN?'))
        osc.unconfigure()         #make sure nothing is in cache
        osc.configure_for_skew()  #setup skew measurement for C1-C2, C1-C3, C1-C4
        sleep(0.5)                #make sure scope had the chance to react
        #print(osc.ask('TRLV?'))
        #print(osc.ask('TDIV?'))

        # now start meaasurement
        try:
            while True:
                osc.trigger_stop()
                osc.clear_sweeps()
                osc.trigger_normal()

                # time interval for data acquisition (minimum 10s)
                sleep(20)

                stats1 = osc.get_statistics(1)
                stats2 = osc.get_statistics(2)
                stats3 = osc.get_statistics(3)

                """
                print(stats1['AVG']*1e12,stats1['SIGMA']*1e12)
                print(stats2['AVG']*1e12,stats2['SIGMA']*1e12)
                print(stats3['AVG']*1e12,stats3['SIGMA']*1e12)
                """
                json_body = [
                    {
                        "measurement": "timing",
                        "tags": {
                            "link": "wrs1-wrs2",
                        },
                        "fields": {
                            "skew" : stats1['AVG']*1e12,
                            "skewrms" : stats1['SIGMA']*1e12
                        }
                    }
                ]
                client.write_points(json_body)
                
                json_body = [
                    {
                        "measurement": "timing",
                        "tags": {
                            "link": "wrs1-wrs3",
                        },
                        "fields": {
                            "skew" : stats2['AVG']*1e12,
                            "skewrms" : stats2['SIGMA']*1e12
                        }
                    }
                ]
                client.write_points(json_body)
                
                json_body = [
                    {
                        "measurement": "timing",
                        "tags": {
                            "link": "wrs1-wrs4",
                        },
                        "fields": {
                            "skew" : stats3['AVG']*1e12,
                            "skewrms" : stats3['SIGMA']*1e12
                        }
                    }
                ]
                client.write_points(json_body)
                

                # sleep a bit before the next measurement
                # (we want to record long-term behaviour w/ temp)
                sleep(10)

        except KeyboardInterrupt:
            pass



if __name__ == "__main__":
    main()
