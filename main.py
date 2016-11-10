#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.app import App

try:
    import devslib.cloud as cloud
except:
    import os
    os.system("git clone https://github.com/oukiar/devslib")
    
    import devslib.cloud as cloud
    
from clonator import Clonator

class ClonatorApp(App):
    def build(self):   
        self.icon = 'icon.png'     
        return Clonator()
    
    def on_start(self):
        pass
        
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass
        
    def on_stop(self):
        print("Quiting")
        #cloud.quit()

if __name__ == '__main__':
    app = ClonatorApp()
    app.run()
