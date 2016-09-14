# -*- coding: utf-8 -*-
#HetWeer Versie2.3
import re
import time
import json
from Screens.Console import Console
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Screens.VirtualKeyBoard import VirtualKeyBoard
from urllib import urlretrieve
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Converter.ClockToText import ClockToText
from Components.Pixmap import Pixmap, MovingPixmap
from twisted.web.client import downloadPage, getPage
from Screens.MessageBox import MessageBox
from enigma import ePicLoad, getDesktop, eTimer
from enigma import eLabel, eListboxPythonMultiContent, loadPNG, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER
from Components.AVSwitch import AVSwitch
import urllib2, urllib
import os
from Tools.Directories import resolveFilename, SCOPE_CONFIG, SCOPE_PLUGINS
from Screens.HelpMenu import HelpableScreen
from Components.FileList import FileList
from time import gmtime, strftime, time
import datetime, time
import struct

HetWeerCurVer = 2.3

def icontotext(icon):
    text = ""
    if icon == "a":
        text = "Zonnig / Helder"
    elif icon == "aa":
        text = "Heldere nacht"
    elif icon == "b":
        text = "Zon met (lichte) bewolking"
    elif icon == "bb":
        text = "Lichte bewolking"
    elif icon == "c":
        text = "Zwaar bewolkt"
    elif icon == "cc":
        text = "Zwaar bewolkt"    
    elif icon == "d":
        text = "Wisselvallig met kans op nevel"    
    elif icon == "dd":
        text = "Wisselvallig met kans op nevel"    
    elif icon == "f":
        text = "Zonnig met kans op buien"    
    elif icon == "ff":
        text = "Bewolkt met kans op buien"    
    elif icon == "g":
        text = "Zon met kans op buien of onweer"    
    elif icon == "gg":
        text = "Buien en kans op onweer"    
    elif icon == "j":
        text = "Opklaringen"    
    elif icon == "jj":
        text = "Opklaringen"
    elif icon == "m":
        text = "Zwaar bewolkt / buien mogelijk"       
    elif icon == "mm":
        text = "Zwaar bewolkt / buien mogelijk"       
    elif icon == "n":
        text = "Zon met kans op nevel"       
    elif icon == "nn":
        text = "Helder met kans nevel"       
    elif icon == "q":
        text = "Zwaar bewolkt / hevige buien"       
    elif icon == "qq":
        text = "Zwaar bewolkt / hevige buien"
    elif icon == "r":
        text = "Bewolkt"       
    elif icon == "rr":
        text = "Bewolkt"       
    elif icon == "s":
        text = "Zwaar bewolkt / onweersbuien"       
    elif icon == "ss":
        text = "Zwaar bewolkt / onweersbuien"       
    else:
        text = "Geen info"       
    return text

def winddirtext(dirtext):
    text = ""
    if dirtext == "N":
        text = "Noord"
    elif dirtext == "NO":
        text = "NoorOost"
    elif dirtext == "O":
        text = "Oosten"
    elif dirtext == "ZO":
        text = "ZuidOosten"
    elif dirtext == "Z":
        text = "Zuiden"
    elif dirtext == "ZW":
        text = "ZuidWest"    
    elif dirtext == "W":
        text = "Westen"    
    elif dirtext == "NW":
        text = "NoordWest"    
    return text


def get_image_info(pic):
    data = None
    with open(pic, "rb") as f:
        data = f.read()
    if is_png(data):
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)
    else:
        raise Exception("not a png image")
    return width, height

def is_png(data):
    return (data[:8] == "\211PNG\r\n\032\n"and (data[12:16] == "IHDR"))

def checkInternet():
    try:
        response = urllib2.urlopen("http://google.com", None, 5)
        response.close()
    except urllib2.HTTPError as e:
        return False
    except urllib2.URLError as e:
        return False
    except socket.timeout:
        return False
    else:
        return True

def getScale():
    return AVSwitch().getFramebufferScale()

sz_w = getDesktop(0).size().width()
state = ["","","","","","",""]

SavedLokaleWeer = []

weatherData = []
lockaaleStad = ""
selectedWeerDay = 0
def getLocWeer(iscity=None):
    inputCity = iscity
    global lockaaleStad
    mydata = []
    if inputCity == None or inputCity.lower() == "*" or inputCity.lower() == " *":
        response = urllib.urlopen("http://ip-api.com/json")
        kaas = response.read()
        data = json.loads(kaas)
        inputCity = data["city"]

    lockaaleStad = inputCity
    mydata = inputCity
    response = urllib.urlopen("http://www.buienradar.be/weer/"+mydata)
    kaas = response.read()
    regx = '''data-location="{&quot;id&quot;:(.*?),&quot;name&quot;:&quot;.*?&quot;'''
    match = re.findall(regx, kaas, re.DOTALL)
        
    if len(match) > 0:        
        response = urllib.urlopen("http://api.buienradar.nl/data/forecast/1.1/all/"+match[0])
        kaas = response.read()
        global weatherData
        weatherData = json.loads(kaas)
        return True 
    else:
        return False
        

class weatherMenu(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800: 
        skin = """
        <screen name="weatherMenu" position="fill" flags="wfNoBorder">
            <widget name="titles" position="30,7" size="1860,75" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget><widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
                <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="920,110" size="975,375" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <widget name="mess1" position="884,1034" size="500,30" foregroundColor="green" font="Console;24"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflaghd.png" position="794,114" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflaghd.png" position="794,177" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflaghd.png" position="794,240" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalhd.png" position="794,303" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="blend"/>
            <widget name="key_green" position="678,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
        </screen>"""

    else: 
        skin = """
        <screen name="weatherMenu" position="fill" flags="wfNoBorder">
            <widget name="titles" position="85,30" size="1085,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="630,106" size="650,250" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <widget name="mess1" position="884,1034" size="500,30" foregroundColor="green" font="Console;18"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflagsd.png" position="550,105" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflagsd.png" position="550,148" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflagsd.png" position="550,191" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalsd.png" position="550,234" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/> 
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/>
        </screen>"""
          
   
    titleNames = ["Nederland", "Belgie", "Europa", "WeerInfo"]
    def __init__(self, session, args=None):
        self.session = session
        self["mess1"] = ScrollLabel("")
        self["titles"] = Label(_("HetWeer 2.3"))
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Ok"))
        self.skin = weatherMenu.skin
        Screen.__init__(self, session)
        
        response = urllib2.urlopen("http://www.luxsat.be/hpengine/download_files/version_weerinfo.txt")
        curver = float(response.read())

        if HetWeerCurVer < curver:
            from enigma import eTimer
            self.pausetimer = eTimer()
            self.pausetimer.callback.append(self.HetWeerUpdateMain)
            self.pausetimer.start(500, True)
        list = []
        for x in weatherMenu.titleNames:
            list.append((_(x)))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "green": self.go}, -1)
        dir = "/tmp/HetWeer/"
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    def go(self):
        global state
        index = self["list"].getSelectedIndex()
        state[0] = weatherMenu.titleNames[index]
        if state[0] == "WeerInfo":
            self.session.open(favoritesscreen)
        #elif state[0] == "HetWeer2":
            #self.session.open(weeroverview)
        else:
            self.session.open(weatherMenuSub1)

    def exit(self):
        self.close()

class weeroverview(Screen):
    def __init__(self, session, args = 0):
        dayinfoblok = ""
        global weatherData
        dataDagen = weatherData["days"]
        self.selected = 0
        
        if sz_w > 1800:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                if happydays.get("winddirection"):
                    windkracht = happydays["winddirection"] 
                losticon = "na"
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]    
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="720,114" size="150,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbighd/""" + str(losticon) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="1146,359" size="42,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/""" + str(losticon) + """.png" position=\"""" + str(131 + (248 * day)) + """,522" size="72,72" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,473" size="135,40" zPosition="3" valign="center" halign="left" font="Regular;34" transparent="1"/>
                    <widget name="midtemp2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,600" size="90,54" zPosition="3" font="Regular;48" transparent="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(240 + (248 * day)) + """,616" size="48,36" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(110 + (248 * day)) + """,660" size="214,70" zPosition="3" valign="center" halign="center" font="Regular;24" transparent="1"/>"""

                dataUrr = dataDagen[day]["hours"]
                for data in dataUrr:
                    if data.get("hour") and (data["hour"]-1)%3 == 0:
                        dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(120 + (216 * uurcount)) + """,779" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                        print "maak : "+ str(day)+"|"+str(uurcount)
                        uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(195 + (216 * uur)) + """,779" size="90,36" zPosition="3" valign="center" halign="right" font="Regular;33" transparent="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(120 + (216 * uur)) + """,870" size="180,54" zPosition="3" valign="center" halign="left" font="Regular;48" transparent="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,945" size="120,30" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,986" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/turbinehd.png" position=\"""" + str(119 + (216 * uur)) + """,983" size="38,38" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/druphd.png" position=\"""" + str(120 + (216 * uur)) + """,945" size="15,23" zPosition="3" alphatest="on"/>"""

	        skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/backgroundhd.png" position="center,center" size="1920,1080" zPosition="0" alphatest="on"/>
                    <widget name="yellowdot" position="286,481" size="36,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="3" alphatest="on"/>
                    <widget name="city1" position="608,56" size="705,64" zPosition="3" valign="center" halign="center" font="Regular;48" transparent="1"/>
                    <widget name="bigtemp1" position="930,134" size="353,118" zPosition="3" valign="center" halign="left" font="Regular;108" transparent="1"/>
                    <widget name="bigweathertype1" position="719,312" size="480,40" zPosition="3" valign="center" halign="center" font="Regular;28" transparent="1"/>
                    <widget name="GevoelsTemp1" position="930,256" size="354,40" zPosition="3" valign="center" halign="center" font="Regular;28" transparent="1"/>
                    <widget name="winddir1" position="767,366" size="345,40" zPosition="3" valign="center" halign="center" font="Regular;28" transparent="1"/>""" + dayinfoblok + """
                </screen>"""
        else:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                if happydays.get("winddirection"):
                    windkracht = happydays["winddirection"] 
                losticon = "na"
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="480,76" size="100,100" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbig/""" + str(losticon) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="764,239" size="28,28" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/""" + str(losticon) + """.png" position=\"""" + str(87 + (165 * day)) + """,348" size="48,48" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,315" size="90,24" zPosition="3" valign="center" halign="left" font="Regular;22" transparent="1"/>
                    <widget name="midtemp2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,400" size="60,36" zPosition="3" font="Regular;32" transparent="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(160 + (165 * day)) + """,413" size="32,22" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(77 + (165 * day)) + """,442" size="138,40" zPosition="3" valign="center" halign="center" font="Regular;16" transparent="1"/>""" 

                dataUrr = dataDagen[day]["hours"]
                for data in dataUrr:
                    if data.get("hour") and (data["hour"]-1)%3 == 0:
                        dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(80 + (144 * uurcount)) + """,519" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                        print "maak : "+ str(day)+"|"+str(uurcount)
                        uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(130 + (144 * uur)) + """,519" size="60,24" zPosition="3" valign="center" halign="right" font="Regular;22" transparent="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(80 + (144 * uur)) + """,580" size="120,36" zPosition="3" valign="center" halign="left" font="Regular;32" transparent="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,630" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,657" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" transparent="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/turbine.png" position=\"""" + str(79 + (144 * uur)) + """,655" size="25,25" zPosition="6" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/drup.png" position=\"""" + str(80 + (144 * uur)) + """,630" size="10,15" zPosition="6" alphatest="on"/>"""

	        skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.png" position="center,center" size="1280,720" zPosition="0" alphatest="on"/>
                    <widget name="yellowdot" position="184,314" size="24,24" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="6" alphatest="on"/>
                    <widget name="city1" position="405,37" size="470,36" zPosition="3" valign="center" halign="center" font="Regular;32" transparent="1"/>
                    <widget name="bigtemp1" position="620,88" size="235,76" zPosition="3" valign="center" halign="left" font="Regular;72" transparent="1"/>
                    <widget name="bigweathertype1" position="479,210" size="320,22" zPosition="3" valign="center" halign="center" font="Regular;18" transparent="1"/>
                    <widget name="GevoelsTemp1" position="620,165" size="236,30" zPosition="3" valign="center" halign="center" font="Regular;18" transparent="1"/>
                    <widget name="winddir1" position="511,244" size="230,22" zPosition="3" valign="center" halign="center" font="Regular;18" transparent="1"/>""" + dayinfoblok + """
                </screen>"""
        
        self.session = session
        Screen.__init__(self, session)
        self.skin = skin
        self["city1"] = Label(_(lockaaleStad))
        for day in range(0, 7):
            self["bigWeerIcon1"+str(day)] = Pixmap()
            self["bigWeerIcon1"+str(day)].hide()
            self["bigDirIcon1"+str(day)] = Pixmap()
            self["bigDirIcon1"+str(day)].hide()
        self["bigtemp1"] = Label(_(""))
        self["bigweathertype1"] = Label(_(""))
        self["GevoelsTemp1"] = Label(_(""))
        self["winddir1"] = Label(_("East"))
        self["yellowdot"] = MovingPixmap()
        for uur in range(0, 8):
            self["dayhour3"+str(uur)] = Label(_("00h"))
            self["daytemp3"+str(uur)] = Label(_("--°C"))
            self["daypercent3"+str(uur)] = Label(_("--%"))
            self["dayspeed3"+str(uur)] = Label(_("--km/u"))
            for day in range(0, 7):
                self["dayIcon"+str(day)+str(uur)] = Pixmap()
                self["dayIcon"+str(day)+str(uur)].hide()
        global weatherData
        dataDagen = weatherData["days"]
        for day in range(1,8):
            dagen = dataDagen[day-1]
            iconclass = "na"
            if dagen.get("iconcode"):
                iconclass = dagen["iconcode"]
            info1 = ""
            info2 = ""
            info3 = ""
            info4 = ""
            info5 = ""
            if dagen.get("date"):
                dagen1 = dataDagen[day]
                mydate = dagen1["date"][:-9]
                unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
                info1 += str(strftime("%A", gmtime(unixtimecode))).title()[:2]
                info1 += str(strftime(" %d", gmtime(unixtimecode)))
            if dagen.get("mintemp"):
                info2 += ""+str("%02.0f" % dagen["mintemp"])+"°"
            elif dagen.get("mintemperature"):
                info2 += "" + str("%02.0f" % dagen["mintemperature"])+"°"
            else:
                info2 += "--.-°C"
            if dagen.get("maxtemp"):
                info3 += "" + str("%02.0f" % dagen["maxtemp"])+"°"
            elif dagen.get("maxtemperature"):
                info3 += "" + str("%02.0f" % dagen["maxtemperature"])+"°"
            else:
                info3 += "--.-°C"
            if dagen.get("beaufort"):
                info4 += str(dagen["beaufort"])
            else:
                info4 += "-"
            if dagen.get("windspeed"):
                info5 += str(dagen["windspeed"])+"KM/H"
            else:
                info5 += "--KM/H"    
            self["smallday2"+str(day-1)] = Label(_(info1))
            self["midtemp2"+str(day-1)] = Label(_(info3))
            self["minitemp2"+str(day-1)] = Label(_(info2))
            self["weertype2"+str(day-1)] = Label(_(icontotext(iconclass)))
            self["myActionMap"] = ActionMap(["SetupActions"], {"left": self.left, "right": self.right, "cancel": self.cancel}, -1)
            self.updateFrameselect()
            
    def left(self):
        self.selected -= 1
        self.updateFrameselect()

    def right(self):
        self.selected += 1
        self.updateFrameselect()

    def updateFrameselect(self):
        if self.selected < 0:
            self.selected = 6
        elif self.selected > 6:
            self.selected = 0
        
        if sz_w > 1800:
            self["yellowdot"].moveTo(286+(248*self.selected),481,1)
        else:
            self["yellowdot"].moveTo(184+(165*self.selected),314,1)
        self["yellowdot"].startMoving()
        global weatherData
        dataDagen = weatherData["days"]
                
        temptext = "na"
        if dataDagen[self.selected+0].get("temperature"):
            temptext = dataDagen[self.selected+0]["temperature"]  
        self["bigtemp1"].setText(str(temptext)+"°C")      
                      
        windtext = "na"
        if dataDagen[self.selected+0].get("winddirection"):
            windtext = dataDagen[self.selected+0]["winddirection"]  
        self["winddir1"].setText("Windrichting "+str(winddirtext(windtext)))
               
        typetext = "na"
        if dataDagen[self.selected+0].get("iconcode"):
            typetext = dataDagen[self.selected+0]["iconcode"]  
        self["bigweathertype1"].setText(icontotext(str(typetext))) 
                
        feeltext = "na"
        if dataDagen[self.selected+0].get("feeltemperature"):
            feeltext = dataDagen[self.selected+0]["feeltemperature"]  
        self["GevoelsTemp1"].setText("GevoelsTemp "+str(feeltext)+"°C")
                
        for day in range(0, 7):
            self["bigWeerIcon1"+str(day)].hide()
            self["bigDirIcon1"+str(day)].hide()
        self["bigWeerIcon1"+str(self.selected)].show()
        self["bigDirIcon1"+str(self.selected)].show()
        dataPerUur = weatherData["days"][self.selected]["hours"]
        for perUurUpdate in range(0,8):
            for day in range(0, 7):
                self["dayIcon"+str(day)+str(perUurUpdate)].hide()
            self["dayIcon"+str(self.selected)+str(perUurUpdate)].show()
            if (perUurUpdate*3)+1 < len(dataPerUur):
                self["dayhour3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*3)+1]["hour"])+"h")
                self["daytemp3"+str(perUurUpdate)].setText(str("%02.0f" % dataPerUur[(perUurUpdate*3)+1]["temperature"])+"°C")
                self["daypercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*3)+1]["precipation"])+"%")
                self["dayspeed3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*3)+1]["windspeed"])+"Km/u")
            else:
                self["dayhour3"+str(perUurUpdate)].setText("")
                self["daytemp3"+str(perUurUpdate)].setText("")
                self["daypercent3"+str(perUurUpdate)].setText("")
                self["dayspeed3"+str(perUurUpdate)].setText("")
    def cancel(self):
        self.close(None)

class weatherMenuSub1(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800: 
        skin = """
        <screen name="weatherMenuSub1" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
                <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="840,110" size="975,450" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
        </screen>"""
        
    else: 
        skin = """
        <screen name="weatherMenuSub1" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="560,106" size="650,301" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/>
        </screen>"""
           
    titleNames = ["Buienradar", "Motregenradar", "Onweerradar", "Wolkenradar", "Zonradar", "Satelliet", "Zonkracht-UV"]
    def __init__(self, session, args=None):
        self.session = session
        self["key_red"] = Label(_("Exit"))
        self.skin = weatherMenuSub1.skin
        Screen.__init__(self, session)
        list = []
        for x in weatherMenuSub1.titleNames:
            list.append((_(x)))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)

    def go(self):
        sz_w = getDesktop(0).size().width()
        isSD = sz_w <= 1800
        newView = isSD
        newView = True
        type = weatherMenuSub1.titleNames[self["list"].getSelectedIndex()]
        tt = time.time()
        tt = round(tt / (5 * 60))
        tt = tt * (5 * 60)
        tt -= (5 * 60)
        aantalfotos = 20
        tijdstap = 5
        locurl = ""
        picturedownloadurl = ""
        loctype = ""
        if state[0] == "Belgie":
            if type == "Buienradar":
                loctype = "radarmapbe/png/?t="
            elif type == "Motregenradar":
                loctype = "drizzlemapnl/png/?t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Wolkenradar":
                loctype = "cloudmapnl/png/?t="
                tt -= 60 * 50
                print time.strftime("ttmap - 20%y%m%d%H%M", time.localtime(tt))
                aantalfotos = 10
            elif type == "Zonradar":
                loctype = "sunmapnl/png/?t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Onweerradar":
                loctype = "lightningnl/?ext=png&t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Satelliet":
                loctype = "satvisual2/png/?t="
                tt -= (60 * 60) * 6
                aantalfotos = 15
                tijdstap = 15
            elif type == "Zonkracht-UV":
                loctype = "sunpowereu/png/?t="
                aantalfotos = 20
                tijdstap = 60
        elif state[0] == "Nederland":
            if type == "Buienradar":
                loctype = "radarmapnl/png/?t="
            elif type == "Motregenradar":
                loctype = "drizzlemapnl/png/?t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Wolkenradar":
                loctype = "cloudmapnl/png/?t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Zonradar":
                loctype = "sunmapnl/png/?t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Onweerradar":
                loctype = "lightningnl/?ext=png&t="
                tt -= 60 * 50
                aantalfotos = 10
            elif type == "Satelliet":
                loctype = "satvisual2/png/?t="
                tt -= (60 * 60) * 6
                aantalfotos = 15
                tijdstap = 15
            elif type == "Zonkracht-UV":
                loctype = "sunpowereu/png/?t="
                aantalfotos = 20
                tijdstap = 60
        elif state[0] == "Europa":
            aantalfotos = 8
            tijdstap = 15
            locurl = "eu"
        if state[0] == "Belgie" and newView:
            if type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapbe/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Motregenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Wolkenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Zonradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=50&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            self.session.open(testnew)
        elif state[0] == "Nederland" and newView:
            if type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Motregenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Wolkenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Zonradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=50&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            self.session.open(testnew)
        elif state[0] == "Europa" and newView:
            if type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapeu/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Motregenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Wolkenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Zonradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=50&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            self.session.open(testnew)
        if not newView:
            picturedownloadurl = "http://api.buienradar.nl/image/1.0/" + loctype
            for x in range(0, aantalfotos):
                turl = time.strftime("20%y%m%d%H%M", time.localtime(tt))
                dir = "/tmp/HetWeer/%02d.png" % (aantalfotos - (x + 1))
                tt += tijdstap * 60
                print picturedownloadurl+ turl
                urllib.urlretrieve(picturedownloadurl + turl, dir)
        
            if os.path.exists('/tmp/HetWeer/00.png'):
                try:
                    self.session.open(View_Slideshow, aantalfotos)
                except:
                    return
            else:
                print '00.png doenst exists, go back!'
                return
    def exit(self):
        self.close()
        
class testnew(Screen):
    def __init__(self, session, args=None):
        skin = """
        <screen position="center,center" size="550,512" title="HetWeer">
            <widget name="picd" position="0,0" size="39600,900" pixmap="/tmp/HetWeer/00.png" zPosition="1" alphatest="on"/>
        </screen>"""
                     
        self.session = session
        self.skin = skin
        Screen.__init__(self, session)
        self.slidePicTimer = eTimer()
        self.slidePicTimer.callback.append(self.updatePic)
        self["picd"] = MovingPixmap()
        global pos
        pos = 0
        self.slidePicTimer.start(750)
        self["actions"] = ActionMap(["WizardActions"], {"back": self.close}, -1)

    def updatePic(self):
        global pos	
        self["picd"].moveTo(pos*-550,0,1)
        pos += 1
        if pos >= (get_image_info("/tmp/HetWeer/00.png")[0]/550):
            pos = 0
        self["picd"].startMoving()

    
class favoritesscreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen name="favoritesscreen" position="fill" flags="wfNoBorder">
            <widget name="favor" position="30,7" size="1860,75" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
                <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="840,210" size="900,630" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <widget name="plaatsn" position="840,120" size="375,70" valign="center" halign="left" zPosition="3" foregroundColor="yellow" font="Regular;63" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="blend"/>
            <widget name="key_green" position="678,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yellow34.png" position="1064,1032" size="34,34" alphatest="blend"/>
            <widget name="key_yellow" position="1114,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
        </screen>"""
        
    else:
        skin = """
        <screen name="favoritesscreen" position="fill" flags="wfNoBorder">
            <widget name="favor" position="85,30" size="1085,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19"
            borderColor="black" borderWidth="2" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="560,160" size="600,430" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <widget name="plaatsn" position="560,106" size="375,43" valign="center" halign="left" zPosition="3" foregroundColor="yellow" font="Regular;28" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/> 
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/>  
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yellow26.png" position="695,643" size="26,26" alphatest="on"/>
            <widget name="key_yellow" position="735,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/>
        </screen>"""
                   
    def __init__(self, session, args=None):
        self.session = session
        self.skin = favoritesscreen.skin
        self["favor"] = Label(_("Favoriete Locaties"))
        self["plaatsn"] = Label(_("Locatie:"))
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Locatie +"))
        self["key_yellow"] = Label(_("Locatie -"))
        Screen.__init__(self, session)
        
        file = open('/etc/enigma2/settings', 'r')
        data = file.read()
        x = re.findall(r'primary_skin=(.*?)/skin.xml',data,re.DOTALL)
        for line in file:
            if re.match('Pd1loi-HD-night', line):
                dir = '/tmp/Pd1loi-HD-night/'
            if not os.path.exists(dir):
                os.makedirs(dir)
            else:
                print 'ok'
        file.close()
        
        list = []
        global SavedLokaleWeer
        for x in SavedLokaleWeer:
            list.append((_(str(x))))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "yellow": self.removeLoc, "green": self.addLoc}, -1)

    def exit(self):
        self.close()


    def addLoc(self):
        self.session.openWithCallback(self.searchCity, VirtualKeyBoard, title=(_("Enter plaatsnaam of * voor zoeken op IP")), text=" ")

    def searchCity(self, searchterm = None):
        if searchterm is not None:
            searchterm = " " + searchterm[1:].title()
            global SavedLokaleWeer
            SavedLokaleWeer.append(str(searchterm))
            file = open("/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/location.save", "w")
            for x in SavedLokaleWeer:
                file.write((str(x)+ "\n"))
            file.close()
            print searchterm
            self.close()
            self.close()

    def go(self):
        if len(SavedLokaleWeer)>0:
            global SavedLokaleWeer
            index = self["list"].getSelectedIndex()
            print "index: "+ str(index)
            if getLocWeer(SavedLokaleWeer[index].rstrip()):
                time.sleep(1)
                self.session.open(weeroverview)
                #self.session.open(lokaalTemp)
            else:
                self.session.open(MessageBox, _("Download fout probeer het later opnieuw a.u.b."), MessageBox.TYPE_INFO)
            
    def removeLoc(self):
        if len(SavedLokaleWeer)>0:
            global SavedLokaleWeer
            index = self["list"].getSelectedIndex()
            SavedLokaleWeer.remove(SavedLokaleWeer[index])
            file = open("/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/location.save", "w")
            for x in SavedLokaleWeer:
                file.write(str(x)+"\n")
            file.close()
            self.close()
            self.close()
   

pos = 0

class lokaalTemp(Screen):
    def __init__(self, session, args=None):
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800: 
            skin = """
            <screen name="lokaaltempscreen" position="fill" flags="wfNoBorder"> 
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87" zPosition="0"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget><widget name="listday" position="375,300" size="1065,585" scrollbarMode="showOnDemand" font="Regular;33" itemHeight="39" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list106539.png"/>\n
                <widget name="listdate" position="450,300" size="120,585" scrollbarMode="showOnDemand" font="Regular;33" itemHeight="39" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list54039.png"/>\n
                <widget name="listminmax" position="675,300" size="300,585" scrollbarMode="showOnDemand" font="Regular;33" itemHeight="39" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list54039.png"/>\n
                <widget name="listbeauf" position="1125,300" size="75,585" scrollbarMode="showOnDemand" font="Regular;33" itemHeight="39" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list54039.png"/>\n
                <widget name="listwind" position="1395,300" size="142,585" scrollbarMode="showOnDemand" font="Regular;33" itemHeight="39" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list54039.png"/>\n
                <widget name="label0" position="160,162" size="750,40" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;34"/>
                <widget name="label1" position="375,240" size="120,50" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;44"/>
                <widget name="label2" position="683,240" size="300,50" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;44"/>
                <widget name="label3" position="1020,240" size="270,50" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;44"/>
                <widget name="label4" position="1395,240" size="150,50" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;44"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
                <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" halign="left"/>
            </screen>"""
        
        else: 
            skin = """
            
            <screen name="lokaaltempscreen" position="fill" flags="wfNoBorder"> 
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="listday" position="250,200" size="710,390" scrollbarMode="showOnDemand" font="Regular;22" itemHeight="26" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list105026.png"/>\n
                <widget name="listdate" position="300,200" size="80,390" scrollbarMode="showOnDemand" font="Regular;22" itemHeight="26" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list39026.png"/>\n
                <widget name="listminmax" position="450,200" size="200,390" scrollbarMode="showOnDemand" font="Regular;22" itemHeight="26" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list39026.png"/>\n
                <widget name="listbeauf" position="750,200" size="50,390" scrollbarMode="showOnDemand" font="Regular;22" itemHeight="26" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list39026.png"/>\n
                <widget name="listwind" position="930,200" size="95,390" scrollbarMode="showOnDemand" font="Regular;22" itemHeight="26" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list39026.png"/>\n
                <widget name="label0" position="120,115" size="500,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;22"/>
                <widget name="label1" position="250,160" size="80,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;28"/>
                <widget name="label2" position="455,160" size="200,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;28"/>
                <widget name="label3" position="680,160" size="180,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;28"/>
                <widget name="label4" position="930,160" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;28"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
                <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" halign="left"/>
            </screen>"""

                
        self.session = session
        self.skin = skin
        self["label0"] = Label(_(str("WeerInfo overzicht: "+lockaaleStad)))
        self["label1"] = Label(_("DAG"))
        self["label2"] = Label(_("MIN    MAX"))
        self["label3"] = Label(_("BEAUFORD"))
        self["label4"] = Label(_("WIND"))
        self["key_red"] = Label(_("Exit"))
        Screen.__init__(self, session)
        global weatherData
        dataDagen = weatherData["days"]
        listday = []
        listdate = []
        listminmax = []
        listbeauf = []     
        listwind = []
        
        for dagen in dataDagen:
            info1 = ""
            info2 = ""
            info3 = ""
            info4 = ""
            info5 = ""
            if dagen.get("date"):
                mydate = dagen["date"][:-9]
                unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
                info1 += str(strftime("%A", gmtime(unixtimecode))).title()[:2]
                info2 += str(strftime("%d", gmtime(unixtimecode))) 
                info2 += str(strftime(" %B", gmtime(unixtimecode)))[:4]
            if dagen.get("mintemp"):
                info3 += ""+str("%04.1f" % dagen["mintemp"])+"°C"
            elif dagen.get("mintemperature"):
                info3 += "" + str("%04.1f" % dagen["mintemperature"])+"°C"
            else:
                info3 += "  --.-°C"
            if dagen.get("maxtemp"):
                info3 += "    " + str("%04.1f" % dagen["maxtemp"])+"°C"
            elif dagen.get("maxtemperature"):
                info3 += "    " + str("%04.1f" % dagen["maxtemperature"])+"°C"
            else:
                info3 += "  --.-°C"
            if dagen.get("beaufort"):
                info4 += str(dagen["beaufort"])
            else:
                info4 += "-"
            if dagen.get("windspeed"):
                info5 += str(dagen["windspeed"])+"KM/H"
            else:
                info5 += "  --KM/H"    
                          
            listday.append((_(str(info1))))
            listdate.append((_(str(info2))))
            listminmax.append((_(str(info3))))
            listbeauf.append((_(str(info4))))
            listwind.append((_(str(info5))))
        self["listday"] = MenuList(listday)
        self["listdate"] = MenuList(listdate)
        self["listminmax"] = MenuList(listminmax)
        self["listbeauf"] = MenuList(listbeauf)
        self["listwind"] = MenuList(listwind)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "down": self.down, "up": self.up, "left": self.left, "right": self.right, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)
        self.currentList = "listday"
    
    def up(self):
        self[self.currentList].up()
        self.UpdateListSelection()
    
    def down(self):
        self[self.currentList].down()
        self.UpdateListSelection()
    
    def left(self):
        self[self.currentList].pageUp()
        self.UpdateListSelection()
            
    def right(self):
        self[self.currentList].pageDown()
        self.UpdateListSelection()
    
    def go(self):
        index = self["listday"].getSelectedIndex()
        if index >= 0:
            global selectedWeerDay
            selectedWeerDay = index-1
            self.session.open(lokaalTempSub)

    def exit(self):
        self.close()

    def UpdateListSelection(self):
         self["listday"].moveToIndex(self["listday"].getSelectedIndex())
         self["listdate"].moveToIndex(self["listday"].getSelectedIndex())
         self["listminmax"].moveToIndex(self["listday"].getSelectedIndex())
         self["listbeauf"].moveToIndex(self["listday"].getSelectedIndex())
         self["listwind"].moveToIndex(self["listday"].getSelectedIndex())

class lokaalTempSub(Screen):
    def __init__(self, session, args=None):
        global selectedWeerDay
        icons =""
        global weatherData
        dataDagen = weatherData["days"][selectedWeerDay]
        index = -1
        if dataDagen.get("hours"):
            for data in dataDagen["hours"]:
                if data.get("iconcode") and data.get("hour") and data.get("winddirection") and data["hour"]%2==0:
                    sz_w = getDesktop(0).size().width()
                    if sz_w > 1800:
                        icons += """<ePixmap pixmap = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+str(data["iconcode"])+""".png" position = "680,"""+str((168*2)+(48*index))+"""" size = "48,48" alphatest = "on" zPosition="3"/>\n"""
                        icons += """<ePixmap pixmap = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/"""+str(data["winddirection"])+""".png" position = "1035,"""+str((173*2)+(48*index))+"""" size = "28,28" alphatest = "on" zPosition="3"/>\n"""
                        index += 1 
                    else:
                        icons += """<ePixmap pixmap = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+str(data["iconcode"])+""".png" position = "330,"""+str((93*2)+(48*index))+"""" size = "48,48" alphatest = "on" zPosition="3"/>\n"""
                        icons += """<ePixmap pixmap = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/"""+str(data["winddirection"])+""".png" position = "670,"""+str((98*2)+(48*index))+"""" size = "28,28" alphatest = "on" zPosition="3"/>\n"""
                        index += 1
        
        else:
            icons += """<ePixmap pixmap = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/na.png" position = "600,""" + str((250*2) + (48 *index)) + """" size = "48,48" alphatest = "on" zPosition="3"  />\n"""
        dataDagen = weatherData["days"]
        mydate = dataDagen[selectedWeerDay+1]["date"][:-9]
        unixtimecode = time.mktime(datetime.datetime(int(mydate[:4]), int(mydate[5:][:2]), int(mydate[8:][:2])).timetuple())
        info = str(strftime(" %A", gmtime(unixtimecode))).title()
        info += str(strftime(" %d", gmtime(unixtimecode)))
        info += str(strftime(" %B", gmtime(unixtimecode)))        
        
        global lockaaleStad
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            skin = """
            <screen position="fill" flags="wfNoBorder">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="2"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="label1" position="470,155" size="500,40" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;34"/>
                <widget name="label2" position="493,235" size="80,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label3" position="820,235" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label4" position="1141,235" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label5" position="1390,235" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="list1" position="492,290" size="500,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
		"""+icons+"""
	        <widget name="listtemp" position="815,290" size="360,600" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
		"""+icons+"""
                <widget name="listwind" position="1170,290" size="360,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
                <widget name="listbui" position="1385,290" size="95,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
           </screen>"""
           
        else:
            skin = """
            <screen position="fill" flags="wfNoBorder">
                <widget name="label1" position="50,45" size="500,28" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;22"/>
                <widget name="label2" position="150,85" size="80,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label3" position="470,85" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label4" position="765,85" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="label5" position="1040,85" size="100,36" zPosition="2" transparent="1" foregroundColor="yellow" font="Regular;32"/>
                <widget name="list1" position="142,140" size="500,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
		"""+icons+"""
	        <widget name="listtemp" position="465,140" size="340,600" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
		"""+icons+"""
                <widget name="listwind" position="790,140" size="360,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
                <widget name="listbui" position="1035,140" size="95,610" scrollbarMode="showOnDemand" font="Regular;36" itemHeight="48" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list36048.png"/>\n
           </screen>"""
                        
        self.session = session
        self.skin = skin
        Screen.__init__(self, session)
        self["label1"] = Label(_(str(""+lockaaleStad+info)))
        self["label2"] = Label(_("TIJD"))
        self["label3"] = Label(_("TEMP"))
        self["label4"] = Label(_("WIND"))
        self["label5"] = Label(_("BUIEN"))
               
        huurData = weatherData["days"][selectedWeerDay]
        list1 = []
        listtemp = []
        listwind = []
        listbui = []  
        if huurData.get("hours"):
            for huur in huurData["hours"]:
                info1 = ""
                info2 = ""
                info3 = ""
                info4 = ""
                if huur.get("hour") and huur["hour"]%2==0:
                    info1 = str(huur["hour"])+":00"
                    if huur.get("hour") and huur["hour"] < 10:
                        info1 = "  " + str(huur["hour"])+":00"
                    if huur.get("temperature"):
                        info2 += str(huur["temperature"])+"°C"
                    else:
                        info2 += "--.-°C"
                    if huur.get("winddirection"):
                        info3 +str(huur["winddirection"])
                    else:
                        info3 += ""
                    if huur.get("beaufort"):
                        info3 += " " + str(huur["beaufort"])
                    else:
                        info3 += " -"
                    if huur.get("precipitation") < 10:
                        info4 += "    " + str(huur["precipitation"])+"%"
                    elif huur.get("precipitation") > 9 and huur.get("precipitation") < 100:
                        info4 += "  " + str(huur["precipitation"])+"%"
                    elif huur.get("precipitation") == 100:
                        info4 += str(huur["precipitation"])+"%"
                    else:
                        info4 += "   0%"
                    list1.append((_(str(info1))))
                    listtemp.append((_(str(info2))))
                    listwind.append((_(str(info3))))
                    listbui.append((_(str(info4))))
        self["list1"] = MenuList(list1)
        self["listtemp"] = MenuList(listtemp)
        self["listwind"] = MenuList(listwind)
        self["listbui"] = MenuList(listbui)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "down": self.down, "up": self.up, "left": self.left, "right": self.right, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)
        self.currentList = "list1"
    
    def up(self):
        self[self.currentList].up()
        self.UpdateListSelection()
    
    def down(self):
        self[self.currentList].down()
        self.UpdateListSelection()
    
    def left(self):
        self[self.currentList].pageUp()
        self.UpdateListSelection()
            
    def right(self):
        self[self.currentList].pageDown()
        self.UpdateListSelection()
        
    def go(self):
        self.close()
    
    def exit(self):
        self.close()

    def UpdateListSelection(self):
         self["list1"].moveToIndex(self["list1"].getSelectedIndex())
         self["listtemp"].moveToIndex(self["list1"].getSelectedIndex())
         self["listwind"].moveToIndex(self["list1"].getSelectedIndex())
         self["listbui"].moveToIndex(self["list1"].getSelectedIndex())
         
class InfoBarAspectSelection:
    STATE_HIDDEN = 0
    STATE_ASPECT = 1
    STATE_RESOLUTION = 2

    def __init__(self):
        self["AspectSelectionAction"] = HelpableActionMap(self, "InfobarAspectSelectionActions",
                                                          {
                                                              "aspectSelection": (
                                                                  self.ExGreen_toggleGreen, _("Aspect list...")),
                                                          })
        self.__ExGreen_state = self.STATE_HIDDEN


    def ExGreen_doAspect(self):
        self.__ExGreen_state = self.STATE_ASPECT
        self.aspectSelection()


    def ExGreen_doResolution(self):
        self.__ExGreen_state = self.STATE_RESOLUTION
        self.resolutionSelection()


    def ExGreen_doHide(self):
        self.__ExGreen_state = self.STATE_HIDDEN


    def ExGreen_toggleGreen(self, arg=""):
        if debug: print pluginPrintname, self.__ExGreen_state
        if self.__ExGreen_state == self.STATE_HIDDEN:
            if debug: print pluginPrintname, "self.STATE_HIDDEN"
            self.ExGreen_doAspect()
        elif self.__ExGreen_state == self.STATE_ASPECT:
            if debug: print pluginPrintname, "self.STATE_ASPECT"
            self.ExGreen_doResolution()
        elif self.__ExGreen_state == self.STATE_RESOLUTION:
            if debug: print pluginPrintname, "self.STATE_RESOLUTION"
            self.ExGreen_doHide()


    def aspectSelection(self):
        selection = 0
        tlist = []
        tlist.append((_("Resolution"), "resolution"))
        tlist.append(("", ""))
        tlist.append((_("Letterbox"), "letterbox"))
        tlist.append((_("PanScan"), "panscan"))
        tlist.append((_("Non Linear"), "non"))
        tlist.append((_("Bestfit"), "bestfit"))
        mode = open("/proc/stb/video/policy").read()[:-1]
        if debug: print pluginPrintname, mode
        for x in range(len(tlist)):
            if tlist[x][1] == mode:
                selection = x
        keys = ["green", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.session.openWithCallback(self.aspectSelected, ChoiceBox, title=_("Please select an aspect ratio..."),
                                      list=tlist, selection=selection, keys=keys)


    def aspectSelected(self, aspect):
        if not aspect is None:
            if isinstance(aspect[1], str):
                if aspect[1] == "resolution":
                    self.ExGreen_toggleGreen()
                else:
                    open("/proc/stb/video/policy", "w").write(aspect[1])
                    self.ExGreen_doHide()
        return
  
class View_Slideshow(Screen, InfoBarAspectSelection):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:                
        skin = """
        <screen name="lieverZon" position="center,center" size="1920, 1080" flags="wfNoBorder"> 
            <widget name="pic" position="center,center" size="1080, 1005" zPosition="2" alphatest="on"/>
            <widget name="file" position="1,1" size="1, 1"  />
        </screen>"""
    else:                
        skin = """
        <screen name="lieverZon" position="center,center" size="1280, 720" flags="wfNoBorder"> 
            <widget name="pic" position="center,center" size="720, 670" zPosition="2" alphatest="on"/>
            <widget name="file" position="1,1" size="1, 1"  />
        </screen>"""
        
    def __init__(self, session, pindex, startslide=True):
        self.textcolor = "#ffffff"
        self.bgcolor = "#000000"
        Screen.__init__(self, session)
        InfoBarAspectSelection.__init__(self)
        self["actions"] = ActionMap(
            ["OkCancelActions", "MediaPlayerActions", "DirectionActions", "MovieSelectionActions"],
            {
                "cancel": self.Exit,
                "playpauseService": self.PlayPause,
                "play": self.PlayPause,
                "pause": self.PlayPause,
                "left": self.prevPic,
                "right": self.nextPic,
                "seekFwd": self.nextPic,
                "seekBack": self.prevPic,
            }, -1)

        self["pic"] = Pixmap()
        self["file"] = Label(_(""))
        self.old_index = 0
        self.picfilelist = []
        self.lastindex = pindex - 1
        self.currPic = []
        self.shownow = True
        self.dirlistcount = 0
        self.speed = 15

        devicepath = "/tmp/HetWeer/"
        currDir = devicepath
        self.filelist = FileList(currDir, showDirectories=False, matchingPattern="^.*\.(png)", useServiceRef=False)

        for x in self.filelist.getFileList():
            if x[0][1] == False:
                try:
                    self.picfilelist.append(currDir + x[0][0])
                except:
                    break
            else:
                self.dirlistcount += 1

        self.maxentry = pindex - 1
        self.pindex = pindex - 1
        if self.pindex < 0:
            self.pindex = 0
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)
        self.slideTimer = eTimer()
        self.slideTimer.callback.append(self.slidePic)
        if self.maxentry >= 0:
            self.onLayoutFinish.append(self.setPicloadConf)
        if startslide == True:
            self.PlayPause();


    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara(
            [self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], 0, int(0),
             self.bgcolor])
        if False == False:
            self["file"].hide()
        self.start_decode()


    def ShowPicture(self):
        if self.shownow and len(self.currPic):
            self.shownow = False
            self["file"].setText(self.currPic[0].replace(".png", ""))
            self.lastindex = self.currPic[1]
            self["pic"].instance.setPixmap(self.currPic[2].__deref__())
            self.currPic = []
            self.next()
            self.start_decode()


    def finish_decode(self, picInfo=""):
        ptr = self.picload.getData()
        if ptr != None:
            text = ""
            try:
                text = picInfo.split("\n", 1)
                text = "(" + str(self.pindex + 1) + "/" + str(self.maxentry + 1) + ") " + text[0].split("/")[-1]
            except:
                pass
            self.currPic = []
            self.currPic.append(text)
            self.currPic.append(self.pindex)
            self.currPic.append(ptr)
            self.ShowPicture()


    def start_decode(self):
        self.picload.startDecode(self.picfilelist[self.pindex])


    def next(self):
        self.pindex -= 1
        if self.pindex < 0:
            self.pindex = self.maxentry


    def prev(self):
        self.pindex += 1
        if self.pindex > self.maxentry:
            self.pindex = 0


    def slidePic(self):
        print "slide to next Picture index=" + str(self.lastindex)
        if True == False and self.lastindex == self.maxentry:
            self.PlayPause()
        self.shownow = True
        self.ShowPicture()


    def PlayPause(self):
        if self.slideTimer.isActive():
            self.slideTimer.stop()
        else:
            self.slideTimer.start(self.speed * 100)
            self.nextPic()


    def prevPic(self):
        self.currPic = []
        self.pindex = self.lastindex
        self.prev()
        self.start_decode()
        self.shownow = True


    def nextPic(self):
        self.shownow = True
        self.ShowPicture()


    def Exit(self):

        try:
            self.removedir = "/tmp/HetWeer/"
            start = 0
            print "max files: ", self.maxentry
            print "delete files used"
            if self.maxentry < 10:
                while start < (self.maxentry + 1):
                    pngfile = "/tmp/HetWeer/0" + str(start) + ".png"
                    os.remove(pngfile)
                    start += 1


            elif self.maxentry > 9:
                while start < (self.maxentry + 1):
                    if start < 10:
                        pngfile = "/tmp/HetWeer/0" + str(start) + ".png"
                        os.remove(pngfile)
                        start += 1
                    else:
                        pngfile = "/tmp/HetWeer/" + str(start) + ".png"
                        os.remove(pngfile)
                        start += 1

            print "unlink done"
        except:
            print "ah damn, no files deleted"
            pass

        self.close()


def main(session, **kwargs):
    if checkInternet():
        global SavedLokaleWeer
        SavedLokaleWeer = []
        locdirsave = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/location.save"
        if os.path.exists(locdirsave):
            for line in open(locdirsave):
                location = line.rstrip()
                SavedLokaleWeer.append(location)
        print "start-----------:" + str(SavedLokaleWeer)
        session.open(weatherMenu)
    else:
        session.open(MessageBox, _("Geen internet"), MessageBox.TYPE_INFO)


def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    return PluginDescriptor(name="HetWeer", description="Weersinformatie",
                            icon="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/plugin.png",
                            where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)
