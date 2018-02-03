# -*- coding: utf-8 -*-
#HetWeer4.3
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
from time import gmtime, strftime, time, localtime
import datetime, time
import struct
import math

versienummer = ''
if os.path.exists('/var/lib/opkg/info/enigma2-plugin-extensions-hetweer.control'):
    with open('/var/lib/opkg/info/enigma2-plugin-extensions-hetweer.control') as origin:
        for versie in origin:
            if 'Version: ' not in versie:
                continue
            try:
                versienummer = versie.split('+')[1]
            except IndexError:
                print

#WeerInfoCurVer = 4.3
def transhtml(text):
    text = text.replace('&nbsp;', ' ').replace('&szlig;', 'ss').replace('&quot;', '"').replace('&ndash;', '-').replace('&Oslash;', '').replace('&bdquo;', '"').replace('&ldquo;', '"').replace('&rsquo;', "'").replace('&gt;', '>').replace('&lt;', '<').replace('&shy;', '')
    text = text.replace('&copy;.*', ' ').replace('&amp;', '&').replace('&uuml;', '\xc3\xbc').replace('&auml;', '\xc3\xa4').replace('&ouml;', '\xc3\xb6').replace('&eacute;', 'e').replace('&hellip;', '...').replace('&egrave;', '\xe8').replace('&agrave;', '\xe0').replace('&mdash;', '-')
    text = text.replace('&Uuml;', 'Ue').replace('&Auml;', 'Ae').replace('&Ouml;', 'Oe').replace('&#034;', '"').replace('&#039;', "'").replace('&#34;', '"').replace('&#38;', 'und').replace('&#39;', "'").replace('&#133;', '...').replace('&#196;', '\xc3\x84').replace('&#214;', '\xc3\x96').replace('&#220;', '\xc3\x9c').replace('&#223;', '\xc3\x9f').replace('&#228;', '\xc3\xa4').replace('&#246;', '\xc3\xb6').replace('&#252;', '\xc3\xbc')
    text = text.replace('&#8211;', '-').replace('&#8212;', '\x97').replace('&#8216;', "'").replace('&#8217;', "'").replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8230;', '...').replace('&#8242;', "'").replace('&#8243;', '"')
    text = text.replace('<u>', '').replace('</u>', '').replace('<b>', '').replace('</b>', '').replace('&deg;', '°').replace('&ordm;', '°').replace('&euml;', 'e').replace('<em>', '').replace('</em>', '').replace('&aacute;', 'a').replace('&oacute;', 'o')
    return text

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
        text = "Overwegend   zonnig"
    elif icon == "jj":
        text = "Overwegend   helder"
    elif icon == "m":
        text = "Zwaar bewolkt  buien mogelijk"
    elif icon == "mm":
        text = "Zwaar bewolkt  buien mogelijk"
    elif icon == "n":
        text = "Zon met kans op nevel"
    elif icon == "nn":
        text = "Helder met kans nevel"
    elif icon == "q":
        text = "Zwaar bewolkt  hevige buien"
    elif icon == "qq":
        text = "Zwaar bewolkt  hevige buien"
    elif icon == "r":
        text = "Bewolkt"
    elif icon == "rr":
        text = "Bewolkt"
    elif icon == "s":
        text = "Zwaar bewolkt  onweersbuien"
    elif icon == "ss":
        text = "Zwaar bewolkt  onweersbuien"
    elif icon == "t":
        text = "Zwaar bewolkt en zware sneeuwval"
    elif icon == "tt":
        text = "Zwaar bewolkt en zware sneeuwval"
    elif icon == "u":
        text = "Wisselend bewolkt lichte sneeuwval"
    elif icon == "uu":
        text = "Wisselend bewolkt lichte sneeuwval"
    elif icon == "v":
        text = "Zwaar bewolkt lichte sneeuwval"
    elif icon == "vv":
        text = "Zwaar bewolkt lichte sneeuwval"
    elif icon == "w":
        text = "Zwaarbewolkt winterse neerslag"
    elif icon == "ww":
        text = "Zwaarbewolkt winterse neerslag"
    else:
        text = "Geen info"
    return text

def winddirtext(dirtext):
    text = ""
    if dirtext == "N":
        text = "Noord"
    elif dirtext == "NO":
        text = "NoordOost"
    elif dirtext == "O":
        text = "Oost"
    elif dirtext == "ZO":
        text = "ZuidOost"
    elif dirtext == "Z":
        text = "Zuid"
    elif dirtext == "ZW":
        text = "ZuidWest"
    elif dirtext == "W":
        text = "West"
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
        return 0
    return width, height

def is_png(data):
    return (data[:8] == "\211PNG\r\n\032\n"and (data[12:16] == "IHDR"))

def checkInternet():
    try:
        response = urllib2.urlopen("http://google.com", None, 5)
        response.close()
    except urllib2.HTTPError:
        return False
    except urllib2.URLError:
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

weatherData = ["ohka"]
lockaaleStad = ""
selectedWeerDay = 0
def getLocWeer(iscity=None):
    inputCity = iscity
    global lockaaleStad
    mydata = []
    if inputCity == None:
        response = urllib.urlopen("http://ip-api.com/json")
        kaas = response.read()
        data = json.loads(kaas)
        inputCity = data["city"]

    lockaaleStad = inputCity
    mydata = inputCity
    text = mydata.replace(' ', '%20')
    req = urllib2.Request("http://claudck193.193.axc.nl/hetweer.php?cn="+text)
    response = urllib2.urlopen(req)
    kaas = response.read()
    regx = '''(.*?),(.*?),'''
    match = re.findall(regx, kaas, re.DOTALL)

    if match:
        response = urllib.urlopen("http://api.buienradar.nl/data/forecast/1.1/all/"+match[0][0])
        kaas = response.read()
        global weatherData
        weatherData = json.loads(kaas)
        return True
    else:
        return False

def weatherchat(country):
    req = urllib2.Request("http://www.buienradar."+country+"/weerbericht")
    response = urllib2.urlopen(req)
    kaas = response.read()
    kaas = kaas.replace("\t", "").replace("\r", "").replace("\n", "").replace("<strong>", "")
    kaas = kaas.replace("<br />", "").replace("</strong>", "").replace("</a>", "")
    kaas = re.sub("""<a href=".*?">""" , "", kaas)
    regx = '''<div id="readarea" class="description">(.*?)</div>'''
    match = re.findall(regx, kaas, re.DOTALL)
    return match[0]

class startScreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen name="startScreen" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28" borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="920,110" size="975,375" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <widget name="mess1" position="884,1034" size="500,30" foregroundColor="green" font="Console;24"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflaghd.png" position="794,114" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflaghd.png" position="794,177" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflaghd.png" position="794,240" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalhd.png" position="794,303" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="blend"/>
            <widget name="key_green" position="678,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen name="startScreen" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19" borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center"><convert type="ServiceName">Name</convert></widget>
            <widget name="list" position="630,106" size="650,250" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <widget name="mess1" position="884,1034" size="500,30" foregroundColor="green" font="Console;18"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflagsd.png" position="550,105" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflagsd.png" position="550,148" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflagsd.png" position="550,191" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalsd.png" position="550,234" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    titleNames = ["Nederland", "Belgie", "Europa", "WeerInfo"]
    def __init__(self, session):
        self.session = session
        self["mess1"] = ScrollLabel("")
        self["key_red"] = Label("Exit")
        self["key_green"] = Label("Ok")
        #self["key_yellow"] = Label("Update Check")
        self.skin = startScreen.skin
        Screen.__init__(self, session)
        list = []
        for x in startScreen.titleNames:
            list.append((x))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "green": self.go}, -1)
        dir = "/tmp/HetWeer/"
        if not os.path.exists(dir):
            os.makedirs(dir)

    def go(self):
        global state
        index = self["list"].getSelectedIndex()
        state[0] = startScreen.titleNames[index]
        if state[0] == "WeerInfo":
            self.session.open(localcityscreen)
        else:
            self.session.open(weatherMenuSub)

    def exit(self):
        self.close()

    def checkupg(self):
        response = urllib2.urlopen("http://users.telenet.be/caught/version_hetweer.txt")
        curver = float(response.read())

        if WeerInfoCurVer < curver:
            from enigma import eTimer
            self.pausetimer = eTimer()
            self.pausetimer.callback.append(self.htwUpdateMain)
            self.pausetimer.start(500, True)
        else:
            self.session.open(MessageBox, "Momenteel geen update beschikbaar", MessageBox.TYPE_INFO)    
    
    def htwUpdateMain(self):
        self.session.openWithCallback(self.htwinfoUpdate, MessageBox,
                                      "Update beschikbaar, wil je de update toepassen?")
    def htwinfoUpdate(self, htwmupg):
        if htwmupg is True:
            self["mess1"].setText("Package will be Updated")
            try:
                self.session.open(Console, "downloading-installing: HetWeer", ["echo Please wait while Downloading and Installing!!;opkg install -force-overwrite http://users.telenet.be/caught/HetWeer/enigma2-plugin-extensions-hetweer_all.ipk;"]) 
                       
            except (IOError, RuntimeError, NameError):
                self["mess1"].setText("Package was NOT Updated")

class weeroverview(Screen):
    def __init__(self, session):
        dayinfoblok = ""
        global weatherData
        dataDagen = weatherData["days"]
        self.selected = 0

        protemp = []
        peocpic = ""
        try:
            for procdays in dataDagen:
                for prochours in procdays["hours"]:
                    protemp.append(round(prochours["temperature"]))
                if len(protemp) > 3:
                    break
        except:
            pass
        if protemp[0] > protemp[1]:
            peocpic = "tempcold.png"
        elif protemp[0] < protemp[1]:
            peocpic = "temphot.png"
        else:
            peocpic = "tempeven.png"
        print "GE0-------->"+str(protemp[0])
        print "GE1-------->"+str(protemp[1])
        peocpichd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/%s" position="1112,155" size="90,80" zPosition="2" transparent="0" alphatest="blend"/>""" % (peocpic)
        peocpicsd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/%s" position="752,99" size="60,53" zPosition="2" transparent="0" alphatest="blend"/>""" % (peocpic)

        if sz_w > 1800:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="690,114" size="150,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbighd/""" + str(dataUrr) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="1146,359" size="42,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/""" + str(losticon) + """.png" position=\"""" + str(131 + (248 * day)) + """,522" size="72,72" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,473" size="135,40" zPosition="3" valign="center" halign="left" font="Regular;34" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="midtemp2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,600" size="90,54" zPosition="3" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(240 + (248 * day)) + """,616" size="90,36" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(110 + (248 * day)) + """,660" size="214,70" zPosition="3" valign="center" halign="center" font="Regular;24" transparent="1" borderColor="black" borderWidth="2"/>"""

                dataUrr = dataDagen[day]["hours"]
                if day == 0:
                    for data in dataUrr:
                        blocks = len(dataUrr)
                        if len(dataUrr)<8:
                            blocks = 8
                        if data.get("hour") and ((data["hour"]-1)%math.ceil(blocks/8)) == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(120 + (216 * uurcount)) + """,779" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
                else:
                    for data in dataUrr:
                        if data.get("hour") and (data["hour"]-1)%3 == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(120 + (216 * uurcount)) + """,779" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(195 + (216 * uur)) + """,779" size="90,36" zPosition="3" valign="center" halign="right" font="Regular;33" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(120 + (216 * uur)) + """,870" size="180,54" zPosition="3" valign="center" halign="left" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,945" size="120,30" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,986" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/turbinehd.png" position=\"""" + str(119 + (216 * uur)) + """,983" size="38,38" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/druphd.png" position=\"""" + str(120 + (216 * uur)) + """,945" size="15,23" zPosition="3" alphatest="on"/>"""

            skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/backgroundhd.png" position="center,center" size="1920,1080" zPosition="0" alphatest="on"/>
                    <widget source="global.CurrentTime" render="Label" position="1651,37" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1426,68" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="yellowdot" position="286,481" size="36,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="3" alphatest="on"/>
                    <widget name="city1" position="608,56" size="705,64" zPosition="3" valign="center" halign="center" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="bigtemp1" position="897,134" size="353,118" zPosition="3" valign="center" halign="left" font="Regular;108" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="bigweathertype1" position="850,312" size="480,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="GevoelsTemp1" position="901,256" size="354,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="winddir1" position="850,366" size="345,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>""" + peocpichd + dayinfoblok + """
                </screen>"""
        else:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="457,76" size="100,100" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbig/""" + str(dataUrr) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="764,235" size="28,28" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/""" + str(losticon) + """.png" position=\"""" + str(87 + (165 * day)) + """,348" size="48,48" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,315" size="90,24" zPosition="3" valign="center" halign="left" font="Regular;22" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="midtemp2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,398" size="60,36" zPosition="3" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(160 + (165 * day)) + """,411" size="32,22" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(77 + (165 * day)) + """,438" size="138,44" zPosition="3" valign="center" halign="center" font="Regular;16" borderColor="black" borderWidth="1" transparent="1"/>"""

                dataUrr = dataDagen[day]["hours"]
                if day == 0:
                    for data in dataUrr:
                        blocks = len(dataUrr)
                        if len(dataUrr)<8:
                            blocks = 8
                        if data.get("hour") and (data["hour"]-1)%math.ceil(blocks/8) == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(80 + (144 * uurcount)) + """,519" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
                else:
                    for data in dataUrr:
                        if data.get("hour") and (data["hour"]-1)%3 == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(80 + (144 * uurcount)) + """,519" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(130 + (144 * uur)) + """,519" size="60,24" zPosition="3" valign="center" halign="right" font="Regular;22" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(80 + (144 * uur)) + """,580" size="120,36" zPosition="3" valign="center" halign="left" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,630" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,657" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/turbine.png" position=\"""" + str(79 + (144 * uur)) + """,655" size="25,25" zPosition="6" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/drup.png" position=\"""" + str(80 + (144 * uur)) + """,630" size="10,15" zPosition="6" alphatest="on"/>"""

            skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.png" position="center,center" size="1280,720" zPosition="0" alphatest="on"/>
                    <widget source="global.CurrentTime" render="Label" position="1086,11" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="936,31" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="yellowdot" position="184,314" size="24,24" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="6" alphatest="on"/>
                    <widget name="city1" position="405,37" size="470,42" zPosition="3" valign="center" halign="center" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="bigtemp1" position="597,88" size="235,76" zPosition="3" valign="center" halign="left" font="Regular;72" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="bigweathertype1" position="570,208" size="320,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="GevoelsTemp1" position="599,165" size="236,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="winddir1" position="570,240" size="230,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>""" + peocpicsd + dayinfoblok + """
                </screen>"""

        self.session = session
        Screen.__init__(self, session)
        self.skin = skin
        self["city1"] = Label(lockaaleStad)
        for day in range(0, 7):
            self["bigWeerIcon1"+str(day)] = Pixmap()
            self["bigWeerIcon1"+str(day)].hide()
            self["bigDirIcon1"+str(day)] = Pixmap()
            self["bigDirIcon1"+str(day)].hide()
        self["bigtemp1"] = Label("")
        self["bigweathertype1"] = Label("")
        self["GevoelsTemp1"] = Label("")
        self["winddir1"] = Label("East")
        self["yellowdot"] = MovingPixmap()
        for uur in range(0, 8):
            self["dayhour3"+str(uur)] = Label("00h")
            self["daytemp3"+str(uur)] = Label("--°C")
            self["daypercent3"+str(uur)] = Label("--%")
            self["dayspeed3"+str(uur)] = Label("--km/u")
            for day in range(0, 7):
                self["dayIcon"+str(day)+str(uur)] = Pixmap()
                self["dayIcon"+str(day)+str(uur)].hide()
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
                unixtimecode = unixtimecode-(86400)
                info1 += str(strftime("%A", localtime(unixtimecode))).title()[:2]
                info1 += str(strftime(" %d", localtime(unixtimecode)))
            if dagen.get("mintemp"):
                info2 += '{:>3}'.format(str("%.0f" % dagen["mintemp"])+"°")
            elif dagen.get("mintemperature"):
                info2 += '{:>3}'.format( str("%.0f" % dagen["mintemperature"])+"°")
            else:
                info2 += "--.-°C"
            if dagen.get("maxtemp"):
                info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemp"])+"°")
            elif dagen.get("maxtemperature"):
                info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemperature"])+"°")
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
            self["smallday2"+str(day-1)] = Label(info1)
            self["midtemp2"+str(day-1)] = Label(info3)
            self["minitemp2"+str(day-1)] = Label(info2)
            self["weertype2"+str(day-1)] = Label(icontotext(iconclass))
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
        dataPerUur = weatherData["days"][0]["hours"]
        self["bigtemp1"].setText("NA")
        self["bigweathertype1"].setText("na")
        self["GevoelsTemp1"].setText("GevoelsTemp NA°C")
        self["winddir1"].setText("Windrichting NA")
        try:
            self["bigtemp1"].setText('{:>4}'.format(str("%.1f" % dataPerUur[(0)]["temperature"])))
            self["GevoelsTemp1"].setText("GevoelsTemp "+str("%.0f" % dataPerUur[(0)]["feeltemperature"])+"°C")
            self["winddir1"].setText("Windrichting "+str(dataPerUur[(0)]["winddirection"]))		
            self["bigweathertype1"].setText(icontotext(str(dataPerUur[(0)]["iconcode"])))
        except:
            0+0
        feeltext = "na"
        if dataDagen[0].get("feeltemperature"):
            feeltext = dataDagen[0]["feeltemperature"]

        windtext = "na"
        if dataDagen[0].get("winddirection"):
            windtext = dataDagen[0]["winddirection"]


        typetext = "na"
        if dataDagen[0].get("iconcode"):
            typetext = dataDagen[0]["iconcode"]
                        
        dataPerUur = weatherData["days"][self.selected]["hours"]
        self["bigWeerIcon1"+str(0)].show()
        self["bigDirIcon1"+str(0)].show()
        
        for perUurUpdate in range(0,8):
            for day in range(0, 7):
                self["dayIcon"+str(day)+str(perUurUpdate)].hide()
            self["dayIcon"+str(self.selected)+str(perUurUpdate)].show()
            if self.selected == 0:
                jumppoint = int(math.ceil(len(dataPerUur)/8))
            else:
                jumppoint = 3
            if jumppoint<1:
                jumppoint=1    
            print jumppoint
            if (perUurUpdate*jumppoint) < len(dataPerUur):
                self["dayhour3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["hour"])+"h")
                self["daytemp3"+str(perUurUpdate)].setText('{:>4}'.format(str("%.0f" % dataPerUur[(perUurUpdate*jumppoint)]["temperature"])+"°C"))
                self["daypercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["precipation"])+"%")
                self["dayspeed3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["windspeed"])+"Km/u")
            else:
                self["dayhour3"+str(perUurUpdate)].setText("")
                self["daytemp3"+str(perUurUpdate)].setText("")
                self["daypercent3"+str(perUurUpdate)].setText("")
                self["dayspeed3"+str(perUurUpdate)].setText("")
    def cancel(self):
        self.close(None)

class weatherMenuSub(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen name="weatherMenuSub" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28"
            borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="840,110" size="975,800" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen name="weatherMenuSub" position="fill" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19"
            borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="560,106" size="650,600" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    listNamesnl = ["Weerbericht", "Temperatuur", "Buienradar", "Motregenradar", "Onweerradar", "Wolkenradar", "Mistradar", "Hagelradar", "Sneeuwradar", "Zonradar", "Zonkracht-UV", "Satelliet"]
    listNamesbe = ["Weerbericht", "Buienradar", "Motregenradar", "Onweerradar", "Wolkenradar", "Hagelradar", "Sneeuwradar", "Zonradar", "Zonkracht-UV", "Satelliet"]
    listNameseu = ["Weerbericht", "Buienradar", "Onweerradar", "Zonkracht-UV", "Satelliet"]
    def __init__(self, session):
        self.session = session
        self["key_red"] = Label("Exit")
        self.skin = weatherMenuSub.skin
        Screen.__init__(self, session)
        list = []
        self.countries = None 
        if state[0] == "Belgie": 
            self.countries = weatherMenuSub.listNamesbe
        elif state[0] == "Nederland":
            self.countries = weatherMenuSub.listNamesnl
        elif state[0] == "Europa":
            self.countries = weatherMenuSub.listNameseu    
        
        for x in self.countries:
            list.append((x))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)

    def go(self):
        sz_w = getDesktop(0).size().width()
        isSD = sz_w <= 1800
        newView = isSD
        newView = True
        type = self.countries[self["list"].getSelectedIndex()]
        tt = time.time()
        tt = round(tt / (5 * 60))
        tt = tt * (5 * 60)
        tt -= (5 * 60)
        aantalfotos = 20
        tijdstap = 5
        locurl = ""
        picturedownloadurl = ""
        loctype = ""
        
        def openScreenRadar():
            if not type == 'Weerbericht':
                distro = 'unknown'
                try:
                    f = open('/etc/opkg/all-feed.conf', 'r')
                    oeline = f.readline().strip().lower()
                    f.close()
                    distro = oeline.split()[1].replace('-all', '')
                except:
                    pass

                if distro == 'openatv'or distro == 'hdfreaks'or distro == 'openhdf':  
                    self.session.open(radarScreenoatv)
                else:
                    self.session.open(radarScreenop)
                    
        global typename
        global wchat
        global legend
        typename = type
        legend = True 
        if state[0] == "Belgie" and newView:
            if type == "Weerbericht":
                wchat = weatherchat("be/Belgie/weerbericht")
                self.session.open(weathertalk)
            elif type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapbe/?ext=png&l=2&hist=0&forc=90&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Motregenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Wolkenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Zonradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Hagelradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Sneeuwradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=100&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=50&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            if not type == "Weerbericht":
                openScreenRadar()

        elif state[0] == "Nederland" and newView:
            if type == "Weerbericht":
                wchat = weatherchat("nl/Nederland/weerbericht")
                self.session.open(weathertalk)
            elif type == "Temperatuur":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/weathermapnl/?ext=png&l=2&hist=12&forc=1&step=0&type=temperatuur&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Motregenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Wolkenradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Sneeuwradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Mistradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/weathermapnl/?type=zicht&ext=png&l=2&hist=9&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Zonradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=50&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Hagelradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=50&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            if not type == "Weerbericht":
                openScreenRadar()

        elif state[0] == "Europa" and newView:
            if type == "Weerbericht":
                wchat = weatherchat("nl/wereldwijd/europa")
                self.session.open(weathertalk)
            elif type == "Buienradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapeu/?ext=png&l=2&hist=0&forc=50&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Onweerradar":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarcloudseu/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
            elif type == "Satelliet":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=10&forc=1&step=0&type=eu&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            elif type == "Zonkracht-UV":
                urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunpowereu/?ext=png&l=2&hist=0&forc=30&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                legend = False
            if not type == "Weerbericht":
                openScreenRadar()
        
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
                    self.session.open(aantalfotos)
                except:
                    return
            else:
                print '00.png doenst exists, go back!'
                return
    def exit(self):
        self.close(weatherMenuSub)

class weathertalk(Screen):
    def __init__(self, session):
        self.session = session
        sz_w = getDesktop(0).size().width()
        if sz_w > 1800:
            skin = """
            <screen name="weerbericht" position="fill" flags="wfNoBorder">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="PAG" position="1780,940" size="104,52" valign="top" halign="left" zPosition="11" font="Regular;46" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="weerchat" position="150,150" size="1620,794" zPosition="11" font="Regular;46" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
                <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
            </screen>"""

        else:
            skin = """
            <screen name="weerbericht" position="fill" flags="wfNoBorder">
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
                <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                <widget name="PAG" position="1180,580" size="72,36" valign="top" halign="left" zPosition="11" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                <widget name="weerchat" position="100,100" size="1100,500" valign="top" halign="left" zPosition="11" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
                <widget name="key_red" position="185,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            </screen>"""

        Screen.__init__(self, session)
        self.skin = skin
        global wchat
        self.indexpage = 0
        list = []
        regx = '''<p.*?>(.*?)</p>'''
        match = re.findall(regx, wchat, re.DOTALL)
        self.wchattext=match
        try:
            self["weerchat"] = Label(transhtml(match[self.indexpage]))
        except:
            self["weerchat"] = Label("regx aanpassen")
        self["PAG"] = Label("1/"+str(len(self.wchattext)))

        self["actions"] = ActionMap(["WizardActions"], {"left": self.left, "right": self.right, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit}, -1)
        self["key_red"] = Label("Exit")

    def left(self):
        if self.indexpage<=0:
            self.indexpage=0
        else:
            self.indexpage=self.indexpage-1
        self["weerchat"].setText(transhtml(self.wchattext[self.indexpage]))
        self["PAG"].setText(str(self.indexpage+1)+"/"+str(len(self.wchattext)))

    def right(self):
        if self.indexpage>=len(self.wchattext)-1:
            self.indexpage=len(self.wchattext)-1
        else:
            self.indexpage=self.indexpage+1
        self["weerchat"].setText(transhtml(self.wchattext[self.indexpage]))
        self["PAG"].setText(str(self.indexpage+1)+"/"+str(len(self.wchattext)))

    def exit(self):
        self.close(weathertalk)


class radarScreenoatv(Screen):
    def __init__(self, session):
        global pos
        self['radarname'] = Label(typename)
        self.weerpng = '/tmp/HetWeer/00.png'
        picformat = get_image_info('/tmp/HetWeer/00.png')
        if not picformat:
            self.weerpng = '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/busy.png'
            picformat = get_image_info(self.weerpng)
        sz_w = getDesktop(0).size().width()
        legendinfo = ''
        if sz_w > 1800:
	    if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/legende.png" zPosition="6" position="705,545" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="fill" title="HetWeer">
            <widget name="picd" position="685,284" size="39600,900" pixmap="/tmp/HetWeer/00.png" zPosition="1" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,290" size="550,64" zPosition="7" halign="center" transparent="1" font="Regular;30" borderColor="black" borderWidth="2"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/framehdatv.png" zPosition="6" position="center,center" size="1920,1080" alphatest="on"/>
            </screen>"""
	
        else:	
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/legendehd.png" zPosition="6" position="370,222" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="fill" title="HetWeer">
            <widget name="picd" position="365,86" size="19800,512" pixmap="/tmp/HetWeer/00.png" zPosition="1" alphatest="on"/>""" + legendinfo + """
            <widget name="radarname" position="center,94" size="550,64" zPosition="6" halign="center" transparent="1" font="Regular;30" borderColor="black" borderWidth="2"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/framesdatv.png" zPosition="6" position="0,80" size="1280,523" alphatest="on"/>
            </screen>"""
		
        self.session = session
        self.skin = skin
        Screen.__init__(self, session)
        self.slidePicTimer = eTimer()
        self.slidePicTimer.callback.append(self.updatePic)
        self['picd'] = MovingPixmap()
        pos = 0
        self.slidePicTimer.start(750)
        self['actions'] = ActionMap(['WizardActions'], {'back': self.close}, -1)

    def updatePic(self):
        global pos
        if sz_w > 1800:
            self['picd'].moveTo((pos * -550)+685, 284, 1)
	else:
	    global picadjust
            postt=(pos * -550)+365
            if postt<-8000:
                pos=0
            self['picd'].moveTo((pos * -550)+365, 86, 1)
        pos += 1
        try:
            if pos >= get_image_info('/tmp/HetWeer/00.png')[0] / 550:
                pos = 0
        except:
            None
            
        self['picd'].startMoving()


class radarScreenop(Screen):
    def __init__(self, session):
        global typename
        self["radarname"] = Label(typename)
        self.weerpng = "/tmp/HetWeer/00.png"
        picformat= None
        try:
            picformat = get_image_info("/tmp/HetWeer/00.png")
        except:    
            None     
        if not picformat:
            self.weerpng = "/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/busy.png"
            picformat = get_image_info(self.weerpng)
        self.scaler = 1.25
        sz_w = getDesktop(0).size().width()
        global legend
        legendinfo = ""
        if sz_w > 1800:
            self.scaler= 2.0
        if sz_w > 1800:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/legendehd.png" zPosition="6" position="460,630" size="270,333" alphatest="on"/>"""
            skin = """
            <screen position="fill" size=\""""+str(int(550*self.scaler-16))+""","""+str(int(512*self.scaler))+"""">
            <widget name="picd" position="400,28" size=\""""+str(int(picformat[0]*self.scaler))+""","""+str(int(picformat[1]*self.scaler))+"""" zPosition="5" alphatest="on"/>"""+legendinfo+"""
            <widget name="radarname" position="center,50" size="600,72" zPosition="6" halign="center" transparent="1" font="Regular;60" borderColor="black" borderWidth="2"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/framehdop.png" zPosition="6" position="center,center" size="1920,1080" alphatest="on"/>
            </screen>"""
        
        else:
            if legend:
                legendinfo = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/legende.png" zPosition="6" position="326,390" size="180,222" alphatest="on"/>"""
            skin = """
            <screen position="fill" size=\""""+str(int(370*self.scaler-16))+""","""+str(int(512*self.scaler))+"""">
            <widget name="picd" position="305,36" size=\""""+str(int(picformat[0]*self.scaler))+""","""+str(int(picformat[1]*self.scaler))+"""" zPosition="5" alphatest="on"/>"""+legendinfo+"""
            <widget name="radarname" position="center,56" size="400,52" zPosition="6" halign="center" transparent="1" font="Regular;40" borderColor="black" borderWidth="2"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/framesdop.png" zPosition="6" position="center,center" size="1280,650" alphatest="on"/>
            </screen>"""

        self.session = session
        self.skin = skin
        Screen.__init__(self, session)
        self.slidePicTimer = eTimer()
        self.slidePicTimer.callback.append(self.updatePic)
        self["picd"] = MovingPixmap()
        global pos
        pos = 0
        self.Scale = AVSwitch().getFramebufferScale()
        self.slidePicTimer.start(750)
        self["actions"] = ActionMap(["WizardActions"], {"back": self.close}, -1)
        self.PicLoad = ePicLoad()
        self.PicLoadPerformance = ePicLoad()
        self.picPath = self.weerpng
        self.PicLoad.PictureData.get().append(self.DecodePicture1)
        self.onLayoutFinish.append(self.ShowPicture1)
        self.PicLoad.startDecode(self.picPath)
    def DecodePicture1(self, PicInfo = ""):
        if self.picPath is not None:
            ptr = self.PicLoad.getData()
            self["picd"].instance.setPixmap(ptr)

    def ShowPicture1(self):
        if self.picPath is not None:
            self.PicLoad.setPara([
                self["picd"].instance.size().width(),
                self["picd"].instance.size().height(),
                self.Scale[0],
                self.Scale[1],
                0,
                1,
                "#0x000000"])
            self.PicLoad.startDecode(self.picPath)

    def updatePic(self):
        global pos
        if sz_w > 1800:
            self["picd"].moveTo((pos*(-550*self.scaler)-15+415),28,1)
                         
        else:
	    global picadjust
            postt=(pos * -687.5)
            if postt<-8000:
                pos=0
            self['picd'].moveTo((pos *(-550*self.scaler))+300, 36, 1)
        pos += 1
        try:
            if pos >= get_image_info('/tmp/HetWeer/00.png')[0] / (550*self.scaler):
                pos = 0
        except:
            None    
        self['picd'].startMoving()

class localcityscreen(Screen):
    sz_w = getDesktop(0).size().width()
    if sz_w > 1800:
        skin = """
        <screen name="localcityscreen" position="fill" flags="wfNoBorder">
            <widget name="favor" position="30,7" size="1860,75" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline87.png" position="0,0" size="1920,87"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,87" size="1920,3" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline3.png" position="0,1020" size="1920,3" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1665,22" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="1440,52" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="30,120" size="720,405" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="30,125" size="720,30" zPosition="1" foregroundColor="white" transparent="1" font="Regular;28"
            borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center">
                <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="840,210" size="900,630" scrollbarMode="showOnDemand" font="Regular;51" itemHeight="63" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list97563.png"/>\n
            <widget name="plaatsn" position="840,120" size="375,70" valign="center" halign="left" zPosition="3" foregroundColor="yellow" font="Regular;63" borderColor="black" borderWidth="1" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red34.png" position="192,1032" size="34,34" alphatest="blend"/>
            <widget name="key_red" position="242,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green34.png" position="628,1032" size="34,34" alphatest="blend"/>
            <widget name="key_green" position="678,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yellow34.png" position="1064,1032" size="34,34" alphatest="blend"/>
            <widget name="key_yellow" position="1114,1030" size="370,38" zPosition="1" transparent="1" font="Regular;34" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    else:
        skin = """
        <screen name="localcityscreen" position="fill" flags="wfNoBorder">
            <widget name="favor" position="85,30" size="1085,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/bigline88.png" position="0,0" size="1280,88"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,88" size="1280,2" zPosition="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/borders/smallline2.png" position="0,630" size="1280,2" zPosition="1"/>
            <widget source="global.CurrentTime" render="Label" position="1070,30" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
            <widget source="global.CurrentTime" render="Label" position="920,50" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
            <widget source="session.VideoPicture" render="Pig" position="85,110" size="417,243" backgroundColor="#ff000000" zPosition="1"/>
            <widget source="session.CurrentService" render="Label" position="85,89" size="417,20" zPosition="1" foregroundColor="white" transparent="1" font="Regular;19"
            borderColor="black" borderWidth="1" noWrap="1" valign="center" halign="center">
            <convert type="ServiceName">Name</convert>
            </widget>
            <widget name="list" position="560,160" size="600,430" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="43" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/list/list65043.png"/>\n
            <widget name="plaatsn" position="560,106" size="375,43" valign="center" halign="left" zPosition="3" foregroundColor="yellow" font="Regular;28" borderColor="black" borderWidth="1" transparent="1"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yellow26.png" position="695,643" size="26,26" alphatest="on"/>
            <widget name="key_yellow" position="735,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    def __init__(self, session):
        self.session = session
        self.skin = localcityscreen.skin
        self["favor"] = Label("Favoriete Locaties")
        self["plaatsn"] = Label("Locatie:")
        self["key_red"] = Label("Exit")
        self["key_green"] = Label("Locatie +")
        self["key_yellow"] = Label("Locatie -")
        Screen.__init__(self, session)
        list = []
        global SavedLokaleWeer
        for x in SavedLokaleWeer:
            list.append((str(x)))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "yellow": self.removeLoc, "green": self.addLoc}, -1)

    def exit(self):
        self.close()

    def addLoc(self):
        self.session.openWithCallback(self.searchCity, VirtualKeyBoard, title=("Enter plaatsnaam e.g. london or london/gb or london_us"), text="")

    def searchCity(self, searchterm = None):
        if searchterm is not None:
            searchterm = "" + searchterm.title()
            SavedLokaleWeer.append(str(searchterm))
            file = open("/etc/enigma2/hetweer.cfg", "w")
            for x in SavedLokaleWeer:
                file.write((str(x)+ "\n"))
            file.close()
            print searchterm
            self.close()
            self.close()

    def go(self):
        if len(SavedLokaleWeer)>0:
            index = self["list"].getSelectedIndex()
            print "index: "+ str(index)
            if getLocWeer(SavedLokaleWeer[index].rstrip()):
                time.sleep(1)
                self.session.open(weeroverview)
            else:
                self.session.open(MessageBox, "Download fout: Controleer spelling of vraag om de plaatsnaam toe te voegen aan de database.", MessageBox.TYPE_INFO)

    def removeLoc(self):
        if len(SavedLokaleWeer)>0:
            index = self["list"].getSelectedIndex()
            SavedLokaleWeer.remove(SavedLokaleWeer[index])
            file = open("/etc/enigma2/hetweer.cfg", "w")
            for x in SavedLokaleWeer:
                file.write(str(x)+"\n")
            file.close()
            self.close()
            self.close()

pos = 0

def main(session, **kwargs):
    if checkInternet():
        global SavedLokaleWeer
        SavedLokaleWeer = []
        locdirsave = "/etc/enigma2/hetweer.cfg"
        if os.path.exists(locdirsave):
            for line in open(locdirsave):
                location = line.rstrip()
                SavedLokaleWeer.append(location)
        print "start-----------:" + str(SavedLokaleWeer)
        response = urllib2.urlopen("http://claudck193.193.axc.nl/wallpapers/daa.php?data")
        ids = int(response.read())
        with open('/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.txt', 'rb') as f:
            data = f.read()
        if not int(data) == ids:
            urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/backgroundhd.png')
            urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php?small', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.png')
	    urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php?data', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.txt')
        session.open(startScreen)
    else:
        session.open(MessageBox, "Geen internet", MessageBox.TYPE_INFO)

def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    return PluginDescriptor(name="HetWeer", description="BuienRadar & WeerInfo, versie " + versienummer,
                            icon="Images/weerinfo.png",
                            where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)
