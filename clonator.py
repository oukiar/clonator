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

hd_blacklist = ['6VPEASNP', '5YD3JQBN', 'Z1D3CPFY', '35TASD0PS']

hd_masters_list = ['63JGPN7GT', 'W1F2HP05']

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
        
        if os.path.isdir('/mnt/DEVS'):
            self.imagespath = '/mnt/DEVS'
        elif os.path.isdir('/home/erik/DEVSDATA'):
            self.imagespath = '/home/erik/DEVSDATA'
        elif os.path.isdir('/mnt/DATA'):
            self.imagespath = '/mnt/DATA'
        else: 
            try:
                self.imagespath = "./"
                os.mkdir("IMAGES")
            except:
                pass

            
        self.imgfiles = ImageFiles(imagespath=os.path.join(self.imagespath, 'IMAGES'))
        
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
            
        elif value == "Escanear con antivirus":
            
            self.model_dst.text = "Model: " + "AV SCAN"
            self.serial_dst.text = "S/N: " + "AV SERIAL SCAN"
            
            self.devdst = value
        else:
            model, sn = get_hd_info(value)
            
            self.model_dst.text = "Model: " + model
            self.serial_dst.text = "S/N: " + sn
            
            self.devdst = value
            
        
        
    def iniciar_clonacion(self):
        
        #checar si se va a escanear
        if self.devdst == "Escanear con antivirus":
            print("Iniciando escaneo usando clamscan")
        
        else:
            Clock.schedule_interval(self.copy_block, 0)
            
            self.f_devsrc = open(self.devsrc, 'rb')
            
            if self.ids.comparacion.active:
                self.f_devdst = open(self.devdst, 'rb') #unbuffered        
            else:
                self.f_devdst = open(self.devdst, 'wb', 0) #unbuffered        
            
            
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
        
        try:
            
            blk = self.f_devsrc.read(self.sizeblock)
            if blk != '':
                
                if self.ids.comparacion.active:
                    
                    print("Leyendo bloque en destino")
                    blk2 = self.f_devdst.read( self.sizeblock )
                    
                    if blk != blk2:
                        print("Error: Los discos no son iguales")
                        
                        #detener
                
                    
                
                
                else:
                    
                    self.f_devdst.write( blk )
                    
                    #si esta habilitada la escritura 4 veces
                    if self.ids.regenerar.active:
                        #1
                        #regresar el puntero de archivo
                        self.f_devdst.seek(-self.sizeblock, 1)
                        #escribir nuevamente el bloque de datos
                        self.f_devdst.write( blk )
                        #self.f_devdst.flush()
                        #os.fsync(self.f_devdst.fileno() )
                        
                        #2
                        #regresar el puntero de archivo
                        self.f_devdst.seek(-self.sizeblock, 1)
                        #escribir nuevamente el bloque de datos
                        self.f_devdst.write( blk )
                        
                        #3
                        #regresar el puntero de archivo
                        self.f_devdst.seek(-self.sizeblock, 1)
                        #escribir nuevamente el bloque de datos
                        self.f_devdst.write( blk )
                        
                        #4
                        #regresar el puntero de archivo
                        self.f_devdst.seek(-self.sizeblock, 1)
                        #escribir nuevamente el bloque de datos
                        self.f_devdst.write( blk )
                        
                        print("Escritura cuadruple de regeneracion correcta")
                        

                
            else:
                #COPIA FINALIZADA
                if self.apagar.active == True:
                    os.system("poweroff")
                else:
                    #self.alarm()
                    Video(source='alarm.mp4', state='play', options={'eos':'loop'})
                    self.lb_info.text = 'Clonacion terminada, ya puede apagar el equipo'
                    Clock.unschedule(self.copy_block)
                    self.clonando = False
        except:
            print("Error en copia: " + str(self.curblock) )
            return
            #COPIA FINALIZADA CON ALGUN ERROR
            if self.apagar.active == True:
                os.system("poweroff")
            else:
                #self.alarm()
                Video(source='alarm.mp4', state='play', options={'eos':'loop'})
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
        
        #si el origen es particion, agregar opcion de pasar antivirus
        hds.append('Escanear con antivirus')
        
        
        return hds


if __name__=='__main__':
    from kivy.base import runTouchApp
    
    runTouchApp(Clonator(orientation='vertical'))
