#MAP System Online Decoder
#from pyplexdo import PyPlexDO, DODigitalOutputInfo
from pyplexclientts import PyPlexClientTSAPI, PL_SingleWFType, PL_ExtEventType
import time
import numpy
from decimal import Decimal
from collections import Counter

#TODO: CSV for channels. Include post time window of event. Need to save population response (dict? key as event_count) from an event  so that they are all saved.




class PSTH: ###Initiate PSTH with desired parameters, creates unit_dict which has wanted units and will catch timestamps from plexon.
    def __init__(self, channel_dict, pre_time, post_time, bin_size):
        self.pre_time = pre_time
        self.post_time = post_time
        self.bin_size = bin_size
        self.total_bins = int((post_time + abs(pre_time)) / bin_size) #bins
        self.channel_dict = channel_dict
        self.unit_dict = {}
        self.pop_total_response = {}
        self.psth_templates = {}
        self.pop_current_response = []
        self.event_ts_list = []
        self.event_number_list = []
        self.total_units = 0
        self.event_count = 0
        self.current_ts = 0
        self.responses = 0 ### testing number of responses
        for chan, unit_list in self.channel_dict.items():
            if chan not in self.unit_dict.keys():
                self.unit_dict[chan] = {}
            for unit in unit_list:
                self.unit_dict[chan][unit] = []
                self.total_units = self.total_units + 1
    ###### build_unit will be used to gather timestamps from plexon and add them to the unit_dict which will be used to compare psth formats, etc.
    def build_unit(self, tmp_channel, tmp_unit, tmp_timestamp):
        self.unit_dict[tmp_channel][tmp_unit].append(Decimal(tmp_timestamp).quantize(Decimal('1.0000')))

    def event(self, event_ts, event_unit):
        #Need to check that it's not a duplicate event...
        if (event_ts - self.current_ts) > 1:        
            self.event_count = self.event_count + 1                             #Total count of events (number of events that occurred)
            self.current_ts = event_ts                                          #Timestamp of the current event
            self.current_event = event_unit                                     #Event number of the current event
            self.event_ts_list.append(event_ts)                                 #List of timestamps
            self.event_number_list.append(event_unit)                           #List of event number


    def psth(self):
        ### Create relative response from population on given trial
        ### Relative response dimensions:
        ### unit:total bins #population: units * total bins
        #OK to call unit_event_response here since we don't need to save it, data is saved to pop_event_response
        pop_trial_response = []
        self.index = 0
        #self.population_response = numpy.zeros(shape=(1, (self.total_units * self.total_bins))) #Create a pop_response template to be filled by bins from neurons
        self.population_response = []
        for chan in self.unit_dict: 
            for unit in self.unit_dict[chan]:
                unit_ts = numpy.asarray(self.unit_dict[chan][unit], dtype = 'float')
                trial_ts = self.current_ts
                offset_ts = unit_ts - trial_ts
                offset_ts = [Decimal(x).quantize(Decimal('1.0000')) for x in offset_ts]
                self.binned_response = numpy.histogram(numpy.asarray(offset_ts, dtype='float'), self.total_bins, range = (-abs(self.pre_time), self.post_time))[0]
                self.population_response = [self.population_response, self.binned_response]
                self.population_response[(self.total_bins*self.index):(self.total_bins*(self.index+1))] = self.binned_response   #### These values will give the total bins (currently: 5) for each neuron (unit)
                pop_trial_response = [x for x in self.population_response]
                self.index = self.index + 1
                if self.index == self.total_units:
                    if self.current_event not in self.pop_total_response.keys():
                        self.pop_total_response[self.current_event] = pop_trial_response
                    else:
                        self.pop_total_response[self.current_event].extend(pop_trial_response)
                    self.pop_current_response = pop_trial_response

    def psthtemplate(self): #Reshape into PSTH format Trials x (Neurons x Bins) Used at the end of all trials.
        self.event_number_count = Counter()
        for num in self.event_number_list:
            self.event_number_count[num] += 1

        for event in self.pop_total_response.keys():
            self.psth_templates[event] = numpy.reshape(self.pop_total_response[event],(self.event_number_count[event], self.total_units*self.total_bins))
            self.psth_templates[event] = self.psth_templates[event].sum(axis = 0) / len(self.psth_templates[event])

    def Test(self):
        print('test')
        # print(self.unit_dict)
        #print(self.event_ts_list)
        print(self.event_number_list)
        print(self.pop_total_response)
        print(self.psth_templates)
        return self.psth_templates, self.pop_total_response



if __name__ =='__main__':
    # Create instance of API class
    channel_dict = {8: [2], 9: [1,2], 20: [2], 22: [2,3]} #New Format to compare Channel and Unit. 0 is unsorted
    pre_time = 1 #seconds (This value is negative or whatever you put, ex: put 0.200 for -200 ms)
    post_time = 1 #seconds
    bin_size = 0.5 #seconds
    # pre_total_bins = 200 #bins
    # post_total_bins = 200 #bins
    wait_for_timestamps = False
    calculate_PSTH = False
    psthtest = PSTH(channel_dict, pre_time, post_time, bin_size)
    
    ##Setup for Plexon DO
    # compatible_devices = ['PXI-6224', 'PXI-6259']
    # plexdo = PyPlexDO()
    # doinfo = plexdo.get_digital_output_info()
    # device_number = None
    # for i in range(doinfo.num_devices):
    #     if plexdo.get_device_string(doinfo.device_numbers[i]) in compatible_devices:
    #         device_number = doinfo.device_numbers[i]
    # if device_number == None:
    #     print("No compatible devices found. Exiting.")
    #     sys.exit(1)
    # else:
    #     print("{} found as device {}".format(plexdo.get_device_string(device_number), device_number))
    # res = plexdo.init_device(device_number)
    # if res != 0:
    #     print("Couldn't initialize device. Exiting.")
    #     sys.exit(1)
    # plexdo.clear_all_bits(device_number)
    ##End Setup for Plexon DO
    
    client = PyPlexClientTSAPI()
    time.sleep(.5)
    # Connect to OmniPlex Server
    client.init_client()

    running = True
    print('running')
    running = True
    timer_list = []
    try:
        while running:
            # Wait half a second for data to accumulate
            if wait_for_timestamps:
                time.sleep(post_time)
                calculate_PSTH = True

            else:
                time.sleep(.5)

            # Get accumulated timestamps
            res = client.get_ts()

            # Print information on the data returned
            tic = time.time()
            for t in res:
                # Print information on spike channel 1
                if t.Type == PL_SingleWFType and t.Channel in psthtest.channel_dict.keys() and t.Unit in psthtest.channel_dict[t.Channel]:
                    print(('Spike Ts: {}s\t Ch: {} Unit: {} Type {}').format(t.TimeStamp, t.Channel, t.Unit, t.Type))
                    psthtest.build_unit(t.Channel,t.Unit,t.TimeStamp)
                # Print information on events
                if t.Type == PL_ExtEventType:
                    print(('Event Ts: {}s Ch: {} Type: {}').format(t.TimeStamp, t.Channel, t.Type))
                    if t.Channel == 257: #Channel for Strobed Events.
                        psthtest.event(t.TimeStamp, t.Unit)
                        psthtest.responses += 1
                        wait_for_timestamps = True
                        #time.sleep(post_time) #Need something to wait for posttime before calculating psth
                        # psthtest.psth()
                    # If Keyboard Event 8 (event channel 108) is found, stop the loop
                    if t.Channel == 108:
                        running = False
                        psthtest.psthtemplate()
            if calculate_PSTH == True:
                psthtest.psth()
                wait_for_timestamps = False
                calculate_PSTH = False
            toc = time.time() - tic
            timer_list.append(toc)

                       

    except KeyboardInterrupt:
        running = False
        psthtest.psthtemplate()
    print('close')
    client.close_client()

    x , y = psthtest.Test()
