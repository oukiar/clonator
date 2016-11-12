#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.clock import Clock

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.video import Video
from kivy.uix.popup import Popup

from kivy.properties import StringProperty

import os, time

from hdutils import get_hd_info

from devslib.scrollbox import ScrollBox

hd_blacklist = ['6VPEASNP', '5YD3JQBN', 'Z1D3CPFY']

hd_masters_list = ['63JGPN7GT']

class DMesg(TextInput):
    pass
    
class ImageName(Popup):
    pass
        
    
class ImageFiles(Popup):
    pass
        
    
class Clonator(FloatLayout):
    
    def __init__(self, **kwargs):
        super(Clonator, self).__init__(**kwargs)
        
        self.imgfile_selected = ""
        
        self.clonando = False
        
        self.curblock = 0
        self.sizeblock = 2**23   # 2 elevado a la 22 == 4MB
        
        #llenar lista de discos duros origen
        self.origen.values = self.list_disks_src()
        
        self.destino.values = self.list_disks_dst()
        
        self.imagespath = '/mnt/DEVS'
        self.imgfiles = ImageFiles(imagespath=self.imagespath)
        
        self.imagename = ImageName()
        
        try:
            #llenar lista de imagenes        
            for i in os.listdir(os.path.join(self.imagespath, 'IMAGES') ):
                button = Button(text=i, height=50)
                button.bind(on_press=self.on_select_image)
                self.imgfiles.items.add_widget(button)
        except:
            pass
        
        
    def set_image_name(self):
        '''
        Seleccion de nombre para imagen destino
        '''
        #actualizar info
        self.model_dst.text = "Archivo de imagen"
        self.serial_dst.text = self.imagename.txt_imagename.text
        
        
        self.devdst = os.path.join(self.imagespath, 'IMAGES', 
                            self.imagename.txt_imagename.text)
                            
        self.imagename.dismiss()
        
    def on_select_image(self, w):
        '''
        Seleccion de archivo de imagen origen
        '''
        
        self.imgfile_selected = w.text
        
        self.imgfiles.dismiss()
        
        #actualizar info
        self.model_src.text = "Archivo de imagen"
        self.serial_src.text = self.imgfile_selected
        
        self.devsrc = os.path.join(self.imagespath, 'IMAGES', 
                            self.imgfile_selected)
        
    def set_origen(self, value):
        #print(value)
        
        if value == "Archivo de imagen":
            #abrir dialogo con la lista de imagenes disponibles
            self.imgfiles.open()
            return
            
        elif value == "/dev/zero":

            self.model_src.text = "Model: " + "0000"
            self.serial_src.text = "S/N: " + "0000"
            
            self.devsrc = value
                        
        else:
            model, sn = get_hd_info(value[:8])
            
            self.model_src.text = "Model: " + model
            self.serial_src.text = "S/N: " + sn
        
            self.devsrc = value
        
    def set_destino(self, value):
        #print(value)
        
        if value == "Archivo de imagen":
            #abrir dialogo para especificar el nombre del archivo de imagen a generar
            self.imagename.open()
            
        elif value == "/dev/null":

            self.model_dst.text = "Model: " + "NULL"
            self.serial_dst.text = "S/N: " + "NULL"
            
            self.devdst = value
            
        else:
            model, sn = get_hd_info(value)
            
            self.model_dst.text = "Model: " + model
            self.serial_dst.text = "S/N: " + sn
            
            self.devdst = value
            
        
        
    def iniciar_clonacion(self):
        Clock.schedule_interval(self.copy_block, 0)
        
        self.f_devsrc = open(self.devsrc, 'rb')
        self.f_devdst = open(self.devdst, 'wb')        
        
        self.f_devsrc.seek(int(self.inicio.text), 0)
        self.f_devdst.seek(int(self.inicio.text), 0)
        
        self.init_time = time.time()
        
        self.clonando = True
        
    
    def copy_block(self, dt):
        '''
        Copia de datos - bloques
        '''
        
        self.curblock += 1
        
        print 'Copiado: ', self.curblock
        
        copied = self.curblock * self.sizeblock
        copied_mb = int(copied / 2**20)
        elapsed = int(time.time() - self.init_time)
        
        if elapsed > 0:
            mbs = int( (copied / elapsed) / 2**20 )
        else: mbs = 0
        
        self.lb_info.text = 'Copiados: ' + str( copied_mb ) + ' MB' + '\nTiempo transcurrido: ' + str(elapsed) + '\nVelocidad: ' + str(mbs) + ' MB/seg'
                
        blk = self.f_devsrc.read(self.sizeblock)
        if blk != '':
            self.f_devdst.write( blk )
        else:
            self.alarm()
            Video(source='alarm.mp3', state='play', options={'eos':'loop'})
            self.lb_info.text = 'Clonacion terminada, ya puede apagar el equipo'
            Clock.unschedule(self.copy_block)
            self.clonando = False

        
    def list_disks_src(self):
        basepath = '/dev/sd'
        hds=[]
        for i in range(ord('a'), ord('z')+1):
            dev = basepath + chr(i)
            try:
                with open(dev):
                    model, sn = get_hd_info(dev)
                    
                    if (model, sn) != (None,None) and sn not in hd_blacklist:
                        
                        #hds.append('Dev:' + dev + '     Model:' + model + '     SN:' + sn)
                        hds.append( dev )
                        
                        
                        #obtener posibles particiones de este disco duro
                        for j in range(1,9):
                            part = dev + str(j)
                            try:
                                with open( part ):
                                    hds.append(part)
                                    
                            except:
                                continue
                                    
            except:
                continue
                
        #agregar zero como origen
        hds.append('/dev/zero')
        
        #agregar imagen como origen
        hds.append('Archivo de imagen')
        
                
        return hds
        
    def list_disks_dst(self):
        basepath = '/dev/sd'
        hds=[]
        for i in range(ord('a'), ord('z')+1):
            dev = basepath + chr(i)
            try:
                with open(dev):
                    model, sn = get_hd_info(dev)
                    
                    if (model, sn) != (None,None):
                        if sn not in hd_masters_list and sn not in hd_blacklist:
                            hds.append(dev)
                            
                            #checar que particiones pueden usarse como destino
                        
                            #obtener posibles particiones de este disco duro
                            for j in range(1,9):
                                part = dev + str(j)
                                try:
                                    with open( part ):
                                        hds.append( part)
                                        
                                except:
                                    continue                            
                            
            except:
                continue
                
        #agregar destino null
        hds.append('/dev/null')

        #agregar opcion de imagen como destino
        hds.append('Archivo de imagen')
        
        return hds


if __name__=='__main__':
    from kivy.base import runTouchApp
    
    runTouchApp(Clonator(orientation='vertical'))
