import sys
import Plexon

try:
    from Plexon import PlexClient
    
    print('PlexClient')
except:
    PlexClient = None
    print('No PlexClient')


class testTask:

    def __init__(self):
        self.taskname = ['Tilt Project']
        print('init')
        self.setup()

    def setup(self):
        print('setup')
        self.data = []

        if PlexClient:
            self.plexon = PlexClient.PlexClient()
            print('PlexClient yes')
        else:
            self.plexon = None
            print('PlexClient no')

##        with open(self.parsfile, 'w+') as fp:
##            json.dump(self.pars, fp)

    def teardown(self):
        if self.plexon:
            self.plexon.CloseClient()
            print('Close Client')

##    def save(self):
##        with open((self.outfile, 'w+') as fp:
##            json.dump(self.data, fp)
                  
    def run(self):
        print('run')
        self.initiate = Plexon.PL_InitClient
        self.tsa = Plexon.PL_GetTimeStampArrays
        self.tss = Plexon.PL_GetTimeStampStructures
        self.tst = Plexon.PL_GetTimeStampTick
        #self.save()
        print('saved')

if __name__ == '__main__':
    mytask = testTask()
    mytask.run()
    mytask.teardown()
    print('Done')
    
