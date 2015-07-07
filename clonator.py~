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
from devslib.utils import MessageBox, MessageBoxTime, LabelItem, ngDialog

hd_blacklist = ['6VPEASNP', '5YD3JQBN', 'Z1D3CPFY']

hd_masters_list = ['63JGPN7GT']

class DMesg(TextInput):
    pass
    
class ImageName(ngDialog):
    def __init__(self, **kwargs):
        
        self.layout = BoxLayout(orientation='vertical')
        
        self.txt_imagename = TextInput()
        self.btn_aceptar = Button(text='Aceptar')
        self.btn_cancelar = Button(text='Cancelar')
        self.btn_cancelar.bind(on_press=self.dismiss)
        
        self.layout.add_widget(self.txt_imagename)
        self.layout.add_widget(self.btn_aceptar)
        self.layout.add_widget(self.btn_cancelar)
        
        super(ImageName, self).__init__(title='Nombre de imagen', 
                                        content=self.layout, 
                                        size_hint=(None, None),
                                        size = (400,150),
                                        **kwargs)
        
    
class ImageFiles(ngDialog):
    
    imgfile_selected = StringProperty('')
    
    def __init__(self, **kwargs):
        
        self.imagespath = kwargs.get('imagespath')
        
        self.list_images()
        
        super(ImageFiles, self).__init__(title='Archivos de imagen', 
                                            content = self.box_images,
                                            size_hint=(None, None),
                                            size = (640,600),
                                            **kwargs)
                          
    def list_images(self):
        self.box_images = BoxLayout(orientation='vertical')
        
        for i in os.listdir(os.path.join(self.imagespath, 'IMAGES') ):
            button = Button(text=i)
            button.bind(on_press=self.on_button)
            self.box_images.add_widget(button)
            
        #aceptar y cancelar
        self.btn_cancel = Button(text='Cancelar')
        self.btn_cancel.bind(on_press=self.dismiss)
        self.box_images.add_widget(self.btn_cancel)
            
    def on_button(self, w):
        self.imgfile_selected = w.text
        
    
class Clonator(FloatLayout):
    
    def __init__(self, **kwargs):
        super(Clonator, self).__init__(**kwargs)
        
        self.lay_box = BoxLayout(orientation='vertical')
        
        self.clonando = False
        
        self.curblock = 0
        self.sizeblock = 2**23   # 2 elevado a la 22 == 4MB
        
        self.imagespath = '/media/clonator/DEVS'
        
        #image files
        try:
            self.imgfiles = ImageFiles(imagespath=self.imagespath)
        except:
            self.imgfiles = None
        
        self.hd_src = LabelItem(caption='Origen', itemtype=Spinner, item_kwargs={'text':'Seleccionar origen', 'values':self.list_disks_src()} )
        self.hd_src.item.bind(text=self.on_hd_src)
        self.lay_box.add_widget(self.hd_src)
                
        self.hd_dst = LabelItem(caption='Destino', itemtype=Spinner, item_kwargs={'text':'Seleccionar destino', 'values':self.list_disks_dst()} )
        self.hd_dst.item.bind(text=self.on_hd_dst)
        self.lay_box.add_widget(self.hd_dst)
        
        self.inicio = LabelItem(caption='Inicio', itemtype=TextInput, item_kwargs={'text':'0'} )
        self.lay_box.add_widget(self.inicio)
        
        self.progress = ProgressBar()
        self.lay_box.add_widget(self.progress)
        
        self.lb_info = Label(text='Estado: Listo para iniciar')
        self.lay_box.add_widget(self.lb_info)

        self.btn_iniciar = Button(text='Iniciar')
        self.btn_iniciar.bind(on_press=self.iniciar)
        self.lay_box.add_widget(self.btn_iniciar)

        self.btn_cancelar = Button(text='Cancelar')
        self.btn_cancelar.bind(on_press=self.cancelar)
        self.lay_box.add_widget(self.btn_cancelar)
        
        self.btn_apagar = Button(text='Apagar equipo')
        self.btn_apagar.bind(on_press=self.apagar)
        self.lay_box.add_widget(self.btn_apagar)
        
        self.add_widget(self.lay_box)
        
    def apagar(self, w):
        if self.clonando:        
            self.msg = MessageBox(title='Existe clonacion en curso, confirma que desea apagar el sistema?')
            self.msg.btn_aceptar.bind(on_press=self.apagar_confirmado)
            self.add_widget(self.msg)
            return
            
        os.system('poweroff')
        
    def apagar_confirmado(self, w):            
        os.system('poweroff')   
        
    def on_hd_src(self, w, val):
        self.devsrc = self.get_dev(val)
        
        if self.devsrc == 'IMAGEN':
            self.add_widget(self.imgfiles)
            self.imgfiles.bind(imgfile_selected=self.on_selected_image)
            
    def on_selected_image(self, w, val):
        self.devsrc = os.path.join(self.imagespath, 'IMAGES', val)
        self.remove_widget(self.imgfiles)
        #self.hd_src.item.text = val
        
    def on_hd_dst(self, w, val):
        devdst = self.get_dev(val)
        
        if devdst == 'IMAGEN':
            self.dlg_imagename = ImageName()
            self.dlg_imagename.btn_aceptar.bind(on_press=self.on_imagename)
            
            self.add_widget( self.dlg_imagename )
            return
        
        if val == self.hd_src.item.text:
            self.add_widget(MessageBoxTime(msg='El destino no puede ser el mismo que el origen', duration=2) )
            return
            
        self.devdst = devdst
        
    def on_imagename(self, w):
        '''
        Evento cuando se acepta el archivo destino de imagen
        '''        
        self.devdst = os.path.join(self.imagespath, 'IMAGES', 
                            self.dlg_imagename.txt_imagename.text)
                            
        self.remove_widget( self.dlg_imagename )
        
        
    def get_dev(self, val):
        '''
        Analiza y extrae el archivo-dispositivo seleccionado
        '''
        
        if val == 'Archivo de imagen':
            return 'IMAGEN'
            
        if 'Particion' in val:
            return val.split('Particion: ')[1]
            
        try:
            tokens = val.split('     ')
            dev = tokens[0].split(':')[1]
            model = tokens[1].split(':')[1]
            sn = tokens[2].split(':')[1]
            #w.text = 'Dev: ' + dev + '\nModelo: ' + model + '\nSN: ' + sn
            
            
            return dev
        
        except:
            return val
            
        
    def cancelar(self, w):
        if self.clonando:        
            self.msg = MessageBox(title='Existe clonacion en curso, confirma que desea cancelar la operacion?')
            self.msg.btn_aceptar.bind(on_press=self.cancelar_confirmado)
            self.add_widget(self.msg)
            #self.msg.open()
            return
            
    def cancelar_confirmado(self, w):
        self.lb_info.text = 'Clonacion cancelada'
        Clock.unschedule(self.copy_block)
        self.clonando = False
        self.msg.dismiss()
        
    def iniciar(self, w):
        
        if self.clonando:
            self.add_widget(MessageBoxTime(msg='Ya se esta realizando la clonacion') )
            return
        
        if self.hd_src.item.text == 'Origen' or self.hd_dst.item.text == 'Destino':
            self.lb_info.text = 'ERROR: Debe elejir un origen y un destino'
            return
            
        self.msg = MessageBox(title='Esta seguro que desea iniciar la operacion?', size_hint=(None,None), size=(400,150))
        self.msg.btn_aceptar.bind(on_press=self.iniciar_confirmado)
        self.msg.btn_cancelar.bind(on_press=self.msg.dismiss)
        
        self.msg.open()
        
    def iniciar_confirmado(self, w):
        #extraer dispositivo origen y disp. destino
        Clock.schedule_interval(self.copy_block, 0)
        
        self.f_devsrc = open(self.devsrc, 'rb')
        self.f_devdst = open(self.devdst, 'wb')        
        
        self.f_devsrc.seek(int(self.inicio.item.text), 0)
        self.f_devdst.seek(int(self.inicio.item.text), 0)
        
        self.msg.dismiss()
        
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
            
    def alarm(self):
        pass
        
    def add_commas(self, strnumber):
        init = len(strnumber) % 3
        newstr = strnumber[0:init]
        for i in range(init, len(strnumber), 3):
            newstr += ',' + strnumber[i:i+3]
            
        return newstr
        
    def list_disks(self):
        basepath = '/dev/sd'
        hds=[]
        for i in range(ord('a'), ord('z')+1):
            dev = basepath + chr(i)
            try:
                with open(dev):
                    model, sn = get_hd_info(dev)
                    if (model, sn) != (None,None):
                        hds.append('Dev:' + dev + '     Model:' + model + '     SN:' + sn)
            except:
                continue
        return hds
        
    def list_disks_src(self):
        basepath = '/dev/sd'
        hds=[]
        for i in range(ord('a'), ord('z')+1):
            dev = basepath + chr(i)
            try:
                with open(dev):
                    model, sn = get_hd_info(dev)
                    
                    if (model, sn) != (None,None) and sn not in hd_blacklist:
                        
                        hds.append('Dev:' + dev + '     Model:' + model + '     SN:' + sn)
                        
                        #obtener posibles particiones de este disco duro
                        for j in range(1,9):
                            part = dev + str(j)
                            try:
                                with open( part ):
                                    hds.append('Particion: ' + part)
                                    
                            except:
                                continue
                                    
            except:
                continue
                
        #agregar zero como origen
        hds.append('Dev:' + '/dev/zero' + '     Model:' + 'Zeros' + '     SN:0000')
        
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
                            hds.append('Dev:' + dev + '     Model:' + model + '     SN:' + sn)
                            
                            #checar que particiones pueden usarse como destino
                        
                            #obtener posibles particiones de este disco duro
                            for j in range(1,9):
                                part = dev + str(j)
                                try:
                                    with open( part ):
                                        hds.append('Particion: ' + part)
                                        
                                except:
                                    continue                            
                            
            except:
                continue
                
        #agregar destino null
        hds.append('Dev:' + '/dev/null' + '     Model:' + 'Null' + '     SN:null')

        #agregar opcion de imagen como destino
        hds.append('Archivo de imagen')
        
        return hds


if __name__=='__main__':
    from kivy.base import runTouchApp
    
    runTouchApp(Clonator(orientation='vertical'))
