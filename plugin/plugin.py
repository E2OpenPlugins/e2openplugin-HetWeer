# -*- coding: utf-8 -*-
#HetWeer5.8
import os
import re 
import time
import json
import math
import struct
import gettext
import datetime, time
import urllib2, urllib
from Screens.Console import Console
from Components.Language import language
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
from Tools.Directories import resolveFilename, SCOPE_CONFIG, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Screens.HelpMenu import HelpableScreen
from Components.FileList import FileList
from time import gmtime, strftime, localtime

 
PluginLanguageDomain = "FileBrowser"
PluginLanguagePath = "Extensions/HetWeer/locale/"

lang = language.getLanguage()
os.environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("HetWeer", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/HetWeer/locale/"))

def _(txt):
	t = gettext.dgettext("HetWeer", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

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

#WeerInfoCurVer = 5.8
def transhtml(text):
    text = text.replace('&nbsp;', ' ').replace('&szlig;', 'ss').replace('&quot;', '"').replace('&ndash;', '-').replace('&Oslash;', '').replace('&bdquo;', '"').replace('&ldquo;', '"').replace('&rsquo;', "'").replace('&gt;', '>').replace('&lt;', '<').replace('&shy;', '')
    text = text.replace('&copy;.*', ' ').replace('&amp;', '&').replace('&uuml;', '\xc3\xbc').replace('&auml;', '\xc3\xa4').replace('&ouml;', '\xc3\xb6').replace('&eacute;', 'e').replace('&hellip;', '...').replace('&egrave;', '\xe8').replace('&agrave;', '\xe0').replace('&mdash;', '-')
    text = text.replace('&Uuml;', 'Ue').replace('&Auml;', 'Ae').replace('&Ouml;', 'Oe').replace('&#034;', '"').replace('&#039;', "'").replace('&#34;', '"').replace('&#38;', 'und').replace('&#39;', "'").replace('&#133;', '...').replace('&#196;', '\xc3\x84').replace('&#214;', '\xc3\x96').replace('&#220;', '\xc3\x9c').replace('&#223;', '\xc3\x9f').replace('&#228;', '\xc3\xa4').replace('&#246;', '\xc3\xb6').replace('&#252;', '\xc3\xbc')
    text = text.replace('&#8211;', '-').replace('&#8212;', '\x97').replace('&#8216;', "'").replace('&#8217;', "'").replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8230;', '...').replace('&#8242;', "'").replace('&#8243;', '"')
    text = text.replace('<u>', '').replace('</u>', '').replace('<b>', '').replace('</b>', '').replace('&deg;', '\xb0').replace('&ordm;', '\xb0').replace('&euml;', 'e').replace('<em>', '').replace('</em>', '').replace('&aacute;', 'a').replace('&oacute;', 'o')
    return text

def icontotext(icon):
    text = ""
    if icon == "a":
        text = _("Sunny / Clear")
    elif icon == "aa":
        text = _("Clear night")
    elif icon == "b":
        text = _("Sunny few clouds")
    elif icon == "bb":
        text = _("Light cloudy")
    elif icon == "c":
        text = _("Heavy clouds")
    elif icon == "cc":
        text = _("Heavy clouds")
    elif icon == "d":
        text = _("Changeable and chance of mist")
    elif icon == "dd":
        text = _("Changeable and chance of mist")
    elif icon == "f":
        text = _("Sunny and chance of showers")
    elif icon == "ff":
        text = _("Cloudy and chance of showers")
    elif icon == "g":
        text = _("Sunny and chance of thundershowers")
    elif icon == "gg":
        text = _("Showers and chance of thunder")
    elif icon == "j":
        text = _("Mostly sunny")
    elif icon == "jj":
        text = _("Mostly clear")
    elif icon == "m":
        text = _("Heavy clouds showers possible")
    elif icon == "mm":
        text = _("Heavy clouds showers possible")
    elif icon == "n":
        text = _("Sunny and chance of mist")
    elif icon == "nn":
        text = _("Clear and chance of mist")
    elif icon == "q":
        text = _("Heavy clouds  heavy showers")
    elif icon == "qq":
        text = _("Heavy clouds  heavy showers")
    elif icon == "r":
        text = _("Cloudy")
    elif icon == "rr":
        text = _("Cloudy")
    elif icon == "s":
        text = _("Heavy clouds  thundershowers")
    elif icon == "ss":
        text = _("Heavy clouds  thundershowers")
    elif icon == "t":
        text = _("Heavy clouds and heavy snowfall")
    elif icon == "tt":
        text = _("Heavy clouds and heavy snowfall")
    elif icon == "u":
        text = _("Changeable cloudy light snowfall")
    elif icon == "uu":
        text = _("Changeable cloudy light snowfall")
    elif icon == "v":
        text = _("Heavy clouds light snowfall")
    elif icon == "vv":
        text = _("Heavy clouds light snowfall")
    elif icon == "w":
        text = _("Heavy clouds winter rainfall")
    elif icon == "ww":
        text = _("Heavy clouds winter rainfall")
    else:
        text = _("No info")
    return text

def winddirtext(dirtext):
    text = ""
    if dirtext == "N":
        text = _("N")
    elif dirtext == "NO":
        text = _("NE")
    elif dirtext == "O":
        text = _("E")
    elif dirtext == "ZO":
        text = _("SE")
    elif dirtext == "Z":
        text = _("S")
    elif dirtext == "ZW":
        text = _("SW")
    elif dirtext == "W":
        text = _("W")
    elif dirtext == "NW":
        text = _("NW")
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
def getLocWeer(iscity = None):
    inputCity = iscity
    global lockaaleStad
    mydata = []
    
    lockaaleStad = inputCity
    mydata = inputCity
    match = None 
    try: 
        print(mydata)
        citynumb = int(mydata.split("-")[1])
        print(citynumb)
        response = urllib.urlopen("http://api.buienradar.nl/data/forecast/1.1/all/"+ str(citynumb))
        antw = response.read()
        global weatherData
        weatherData = json.loads(antw)
        return True
    except:
        try:
            text = mydata.replace(' ', '%20')
            req = urllib2.Request("http://claudck193.193.axc.nl/hetweer.php?cn="+text)
            response = urllib2.urlopen(req)
            antw = response.read()
            regx = '''(.*?),(.*?),'''
            match = re.findall(regx, antw, re.DOTALL)     
        except:
            return False

    if match:
        try:
            response = urllib.urlopen("http://api.buienradar.nl/data/forecast/1.1/all/"+match[0][0])
            antw = response.read()
            global weatherData
            weatherData = json.loads(antw)
            return True
        except:
            return False   
    else:
        return False

def weatherchat(country):
    req = urllib2.Request("http://www.buienradar."+country+"/weerbericht")
    response = urllib2.urlopen(req)
    antw = response.read()
    antw = antw.replace("\t", "").replace("\r", "").replace("\n", "").replace("<strong>", "")
    antw = antw.replace("<br />", "").replace("</strong>", "").replace("</a>", "")
    antw = re.sub("""<a href=".*?">""" , "", antw)
    regx = '''<div id="readarea" class="description">(.*?)</div>'''
    match = re.findall(regx, antw, re.DOTALL)
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
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalhd.png" position="794,114" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflaghd.png" position="794,177" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflaghd.png" position="794,240" size="71,49" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflaghd.png" position="794,303" size="71,49" alphatest="on"/>
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
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/lokaalsd.png" position="550,105" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/nlflagsd.png" position="550,148" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/beflagsd.png" position="550,191" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/lo/euflagsd.png" position="550,234" size="47,32" alphatest="on"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/red26.png" position="145,643" size="26,26" alphatest="on"/>
            <widget name="key_red" position="185,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/green26.png" position="420,643" size="26,26" alphatest="on"/>
            <widget name="key_green" position="460,643" size="220,28" zPosition="1" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    titleNames = [_("Local Weather"), _("The Netherlands"), _("Belgium"), _("Europe")]
    def __init__(self, session):
        self.session = session
        self["mess1"] = ScrollLabel("")
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label("OK")
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
        if state[0] == _("Local Weather"):
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
        peocpichd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/%s" position="1112,143" size="90,80" zPosition="2" transparent="0" alphatest="blend"/>""" % (peocpic)
        peocpicsd = """<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/%s" position="752,99" size="60,53" zPosition="2" transparent="0" alphatest="blend"/>""" % (peocpic)

        if sz_w > 1800:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                sunrise = "na"
                sunset = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                    sunrise = (str(dataDagen[0]["sunrise"]).split("T")[1])[:-3]
                    sunset = (str(dataDagen[0]["sunset"]).split("T")[1])[:-3]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="636,102" size="150,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbighd/""" + str(dataUrr) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="1170,343" size="42,42" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/""" + str(losticon) + """.png" position=\"""" + str(131 + (248 * day)) + """,498" size="72,72" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(138 + (248 * day)) + """,461" size="135,40" zPosition="3" valign="center" halign="left" font="Regular;34" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="maxtemp2""" + str(day) + """" position=\"""" + str(130 + (248 * day)) + """,571" size="90,54" zPosition="3" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(240 + (248 * day)) + """,587" size="90,36" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(110 + (248 * day)) + """,617" size="214,70" zPosition="3" valign="center" halign="center" font="Regular;24" transparent="1" borderColor="black" borderWidth="2"/>
                    <widget name="sunriselab" position="625,362" size="200,40" zPosition="3" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/sunupdownhd.png" zPosition="3" position="650,295" size="120,60" alphatest="blend"/>"""
                dataUrr = dataDagen[day]["hours"]
                #create hourly weatherIcon
                if day == 0:
                    for data in dataUrr:
                        blocks = len(dataUrr)
                        if len(dataUrr)<8:
                            blocks = 8
                        if data.get("hour") and ((data["hour"]-1)%math.ceil(blocks/8)) == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(120 + (216 * uurcount)) + """,749" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
                else:
                    for data in dataUrr:
                        if data.get("hour") and (data["hour"]-1)%3 == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(120 + (216 * uurcount)) + """,749" size="72,72" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconhd/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(195 + (216 * uur)) + """,757" size="90,36" zPosition="3" valign="center" halign="right" font="Regular;33" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(120 + (216 * uur)) + """,820" size="180,54" zPosition="3" valign="center" halign="left" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="sunpercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,883" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,922" size="120,30" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="hrdayper3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,961" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(168 + (216 * uur)) + """,1000" size="123,32" zPosition="3" valign="center" halign="left" font="Regular;27" transparent="1" borderColor="black" borderWidth="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/sunpchd.png" position=\"""" + str(114 + (216 * uur)) + """,879" size="36,36" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/rainhd.png" position=\"""" + str(116 + (216 * uur)) + """,921" size="30,30" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/rhhd.png" position=\"""" + str(120 + (216 * uur)) + """,960" size="23,30" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/windhd/turbinehd.png" position=\"""" + str(119 + (216 * uur)) + """,997" size="38,38" zPosition="3" alphatest="on"/>"""
                    
            skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/backgroundhd.png" position="center,center" size="1920,1080" zPosition="0" alphatest="on"/>
                    <widget source="global.CurrentTime" render="Label" position="1651,42" size="225,37" transparent="1" zPosition="1" font="Regular;36" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="1426,73" size="450,37" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="yellowdot" position="294,464" size="36,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="3" alphatest="on"/>
                    <widget name="city1" position="608,44" size="705,64" zPosition="3" valign="center" halign="center" font="Regular;48" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="bigtemp1" position="870,122" size="353,118" zPosition="3" valign="center" halign="left" font="Regular;108" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="bigweathertype1" position="870,298" size="480,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="GevoelsTemp1" position="870,250" size="354,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>
                    <widget name="winddir1" position="870,346" size="345,40" zPosition="3" valign="center" halign="left" font="Regular;28" transparent="1" borderColor="black" borderWidth="1"/>""" + peocpichd + dayinfoblok + """
                </screen>"""
        else:
            for day in range(0, 7):
                uurcount = 0
                dagen = dataDagen[day+1]
                happydays = dataDagen[day]
                windkracht = "na"
                losticon = "na"
                dataUrr = "na"
                sunrise = "na"
                sunset = "na"
                try:
                    windkracht = dataDagen[0]["hours"][0]["winddirection"]
                    dataUrr = dataDagen[0]["hours"][0]["iconcode"]
                    sunrise = (str(dataDagen[0]["sunrise"]).split("T")[1])[:-3]
                    sunset = (str(dataDagen[0]["sunset"]).split("T")[1])[:-3]
                except:
                    0+0
                if happydays.get("iconcode"):
                    losticon = happydays["iconcode"]
                dayinfoblok += """
                    <widget name="bigWeerIcon1""" + str(day) + """" position="422,76" size="100,100" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/iconbig/""" + str(dataUrr) + """.png" zPosition="1" alphatest="on"/>
                    <widget name="bigDirIcon1""" + str(day) + """" position="790,240" size="28,28" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/""" + str(windkracht) + """.png" zPosition="1" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/""" + str(losticon) + """.png" position=\"""" + str(87 + (165 * day)) + """,334" size="48,48" zPosition="3" transparent="0" alphatest="on"/>
                    <widget name="smallday2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,308" size="90,24" zPosition="3" valign="center" halign="left" font="Regular;22" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="maxtemp2""" + str(day) + """" position=\"""" + str(92 + (165 * day)) + """,382" size="60,36" zPosition="3" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="minitemp2""" + str(day) + """" position=\"""" + str(160 + (165 * day)) + """,395" size="32,22" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="weertype2""" + str(day) + """" position=\"""" + str(77 + (165 * day)) + """,416" size="138,44" zPosition="3" valign="center" halign="center" font="Regular;16" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="sunriselab" position="416,248" size="200,40" zPosition="3" font="Regular;18" transparent="1" borderColor="black" borderWidth="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/sunupdownsd.png" zPosition="3" position="426,206" size="120,60" alphatest="blend"/>"""

                dataUrr = dataDagen[day]["hours"]
                #create hourly weatherIcon
                if day == 0:
                    for data in dataUrr:
                        blocks = len(dataUrr)
                        if len(dataUrr)<8:
                            blocks = 8
                        if data.get("hour") and (data["hour"]-1)%math.ceil(blocks/8) == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(80 + (144 * uurcount)) + """,494" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
                else:
                    for data in dataUrr:
                        if data.get("hour") and (data["hour"]-1)%3 == 0:
                            dayinfoblok += """<widget name="dayIcon""" + str(day)+""+str(uurcount)+ """" position=\"""" + str(80 + (144 * uurcount)) + """,494" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/icon/"""+data["iconcode"]+""".png" zPosition="1" alphatest="on"/>"""
                            print "maak : "+ str(day)+"|"+str(uurcount)
                            uurcount += 1
            for uur in range(0, 8):
                dayinfoblok += """
                    <widget name="dayhour3""" + str(uur) + """" position=\"""" + str(130 + (144 * uur)) + """,506" size="60,24" zPosition="3" valign="center" halign="right" font="Regular;22" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="daytemp3""" + str(uur) + """" position=\"""" + str(80 + (144 * uur)) + """,540" size="120,36" zPosition="3" valign="center" halign="left" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="sunpercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,580" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="daypercent3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,606" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="hrdayper3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """ ,632" size="80,20" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="dayspeed3""" + str(uur) + """" position=\"""" + str(112 + (144 * uur)) + """,658" size="82,21" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/sunpcsd.png" position=\"""" + str(76 + (144 * uur)) + """,578" size="24,24" zPosition="3" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/rainsd.png" position=\"""" + str(77 + (144 * uur)) + """,605" size="20,20" zPosition="6" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/rhsd.png" position=\"""" + str(79 + (144 * uur)) + """,632" size="16,20" zPosition="6" alphatest="on"/>
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/wind/turbine.png" position=\"""" + str(79 + (144 * uur)) + """,656" size="25,25" zPosition="6" alphatest="on"/>"""
                    
            skin = """
                <screen position="fill" flags="wfNoBorder">
                    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.png" position="center,center" size="1280,720" zPosition="0" alphatest="on"/>
                    <widget source="global.CurrentTime" render="Label" position="1086,18" size="150,55" transparent="1" zPosition="1" font="Regular;24" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Format:%-H:%M</convert></widget>
                    <widget source="global.CurrentTime" render="Label" position="936,38" size="300,55" transparent="1" zPosition="1" font="Regular;16" borderColor="black" borderWidth="1" valign="center" halign="right"><convert type="ClockToText">Date</convert></widget>
                    <widget name="yellowdot" position="190,308" size="24,24" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/yeldot.png" zPosition="6" alphatest="on"/>
                    <widget name="city1" position="405,37" size="470,42" zPosition="3" valign="center" halign="center" font="Regular;32" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="bigtemp1" position="565,88" size="235,76" zPosition="3" valign="center" halign="left" font="Regular;72" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="bigweathertype1" position="565,208" size="320,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="GevoelsTemp1" position="565,176" size="236,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>
                    <widget name="winddir1" position="565,240" size="230,30" zPosition="3" valign="center" halign="left" font="Regular;18" borderColor="black" borderWidth="1" transparent="1"/>""" + peocpicsd + dayinfoblok + """
                </screen>"""

        self.session = session
        Screen.__init__(self, session)
        self.skin = skin
        self["city1"] = Label(lockaaleStad.split("-")[0])
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
            self["dayhour3"+str(uur)] = Label(_("00h"))
            self["daytemp3"+str(uur)] = Label("--\xb0C")
            self["sunpercent3"+str(uur)] = Label("--%")
            self["daypercent3"+str(uur)] = Label("--%")
            self["hrdayper3"+str(uur)] = Label("--%")
            self["dayspeed3"+str(uur)] = Label(_("--Km/h"))
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
                info2 += '{:>3}'.format(str("%.0f" % dagen["mintemp"])+"\xb0")
            elif dagen.get("mintemperature"):
                info2 += '{:>3}'.format( str("%.0f" % dagen["mintemperature"])+"\xb0")
            else:
                info2 += "--.-\xb0C"
            if dagen.get("maxtemp"):
                info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemp"])+"\xb0")
            elif dagen.get("maxtemperature"):
                info3 += '{:>3}'.format(str("%.0f" % dagen["maxtemperature"])+"\xb0")
            else:
                info3 += "--.-\xb0C"
            if dagen.get("beaufort"):
                info4 += str(dagen["beaufort"])
            else:
                info4 += "-"
            if dagen.get("windspeed"):
                info5 += str(dagen["windspeed"])+_("Km/h")
            else:
                info5 += _("Km/h")
            self["smallday2"+str(day-1)] = Label(info1)
            self["maxtemp2"+str(day-1)] = Label(info3)
            self["minitemp2"+str(day-1)] = Label(info2)
            self["sunriselab"] = Label(sunrise+" - "+sunset)
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
            self["yellowdot"].moveTo(294+(248*self.selected),464,1)
        else:
            self["yellowdot"].moveTo(190+(165*self.selected),308,1)
        self["yellowdot"].startMoving()
        global weatherData
        dataDagen = weatherData["days"]

        temptext = "na"
        if dataDagen[self.selected+0].get("temperature"):
            temptext = dataDagen[self.selected+0]["temperature"]
        dataPerUur = weatherData["days"][0]["hours"]
        self["bigtemp1"].setText("NA")
        self["bigweathertype1"].setText("na")
        self["GevoelsTemp1"].setText(_("Feels Like: ") + "NA\xb0C")
        self["winddir1"].setText(_("Wind direction: ") + "NA")
        try:
            self["bigtemp1"].setText('{:>4}'.format(str("%.1f" % dataPerUur[(0)]["temperature"])))
            self["GevoelsTemp1"].setText(_("Feels Like: ")+str("%.1f" % dataPerUur[(0)]["feeltemperature"])+"\xb0C")
            self["winddir1"].setText(_("Wind direction: ")+str(winddirtext(dataPerUur[(0)]["winddirection"])))		
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
            try:
            
                if (perUurUpdate*jumppoint) < len(dataPerUur):
                    self["dayhour3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["hour"])+_("h"))
                    self["daytemp3"+str(perUurUpdate)].setText('{:>4}'.format(str("%.0f" % dataPerUur[(perUurUpdate*jumppoint)]["temperature"])+"\xb0C"))
                    self["daypercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["precipation"])+"%")
                    self["dayspeed3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["windspeed"])+_("Km/h"))
                    self["sunpercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["sunshine"])+"%")
                    self["hrdayper3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["humidity"])+"%")
                
                else:
                    self["dayhour3"+str(perUurUpdate)].setText("")
                    self["daytemp3"+str(perUurUpdate)].setText("")
                    self["daypercent3"+str(perUurUpdate)].setText("")
                    self["dayspeed3"+str(perUurUpdate)].setText("")
                    self["sunpercent3"+str(perUurUpdate)].setText("")
                    self["hrdayper3"+str(perUurUpdate)].setText("")
            except:
                try:
                    if (perUurUpdate*jumppoint) < len(dataPerUur):
                        self["dayhour3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["hour"])+_("h"))
                        self["daytemp3"+str(perUurUpdate)].setText('{:>4}'.format(str("%.0f" % dataPerUur[(perUurUpdate*jumppoint)]["temperature"])+"\xb0C"))
                        self["daypercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["precipitation"])+"%")
                        self["dayspeed3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["windspeed"])+_("Km/h"))
                        self["sunpercent3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["sunshine"])+"%")
                        self["hrdayper3"+str(perUurUpdate)].setText(str(dataPerUur[(perUurUpdate*jumppoint)]["humidity"])+"%")
                    else:
                        self["dayhour3"+str(perUurUpdate)].setText("")
                        self["daytemp3"+str(perUurUpdate)].setText("")
                        self["daypercent3"+str(perUurUpdate)].setText("")
                        self["dayspeed3"+str(perUurUpdate)].setText("")    
                        self["sunpercent3"+str(perUurUpdate)].setText("")
                        self["hrdayper3"+str(perUurUpdate)].setText("")
                except:
                
                    None
                    
                        
                
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
          
    listNamesnl = [_("Temperature"), _("Rainfall radar"), _("Drizzle"), _("Thunder radar"), _("Clouds radar"), _("Mist radar"), _("Snow radar"), _("Sun radar"), _("Sunpower-UV"), _("Satellite"), _("Weather forecast-nl")]
    listNamesbe = [_("Rainfall radar"), _("Drizzle"), _("Thunder radar"), _("Clouds radar"), _("Hail radar"), _("Snow radar"), _("Sun radar"), _("Satellite"), _("Weather forecast-nl")]
    listNameseu = [_("Rainfall radar"), _("Thunder radar"), _("Satellite"), _("Weather forecast-nl")]
    def __init__(self, session):
        self.session = session
        self["key_red"] = Label(_("Exit"))
        self.skin = weatherMenuSub.skin
        Screen.__init__(self, session)
        list = []
        self.countries = None 
        if state[0] == _("Belgium"): 
            self.countries = weatherMenuSub.listNamesbe
        elif state[0] == _("The Netherlands"):
            self.countries = weatherMenuSub.listNamesnl
        elif state[0] == _("Europe"):
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
            if not type == _("Weather forecast"):
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
        try:
            if state[0] == _("Belgium") and newView:
                if type == _("Weather forecast-nl"):
                    wchat = weatherchat("be/Belgie/weerbericht")
                    self.session.open(weathertalk)
                elif type == _("Rainfall radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapbe/?ext=png&l=2&hist=0&forc=30&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Drizzle"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Clouds radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Sun radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=30&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Thunder radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Hail radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                elif type == _("Snow radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=100&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                elif type == _("Satellite"):
                    urllib.urlretrieve('https://image.buienradar.nl/2.0/image/sprite/SatVisual?height=512&width=550&history=12&skip=0', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Sunpower-UV"):
                    urllib.urlretrieve('https://image.buienradar.nl/2.0/image/sprite/WeatherMapUVIndexNL?extension=png&l=2&hist=0&forc=10&step=0&width=550&height=512', '/tmp/HetWeer/00.png')
                    legend = False
                if not type == _("Weather forecast-nl"):
                    openScreenRadar()

            elif state[0] == _("The Netherlands") and newView:
                if type == _("Weather forecast-nl"):
                    wchat = weatherchat("nl/Nederland/weerbericht")
                    self.session.open(weathertalk)
                elif type == _("Temperature"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/weathermapnl/?ext=png&l=2&hist=2&forc=1&step=0&type=temperatuur&w=550&h=512', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Rainfall radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapnl/?ext=png&l=2&hist=0&forc=30&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Drizzle"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/drizzlemapnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Clouds radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/cloudmapnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Snow radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/snowmapnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                elif type == _("Mist radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/weathermapnl/?type=zicht&ext=png&l=2&hist=2&forc=0&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Sun radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/sunmapnl/?ext=png&l=2&hist=0&forc=30&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Thunder radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/lightningnl/?ext=png&l=2&hist=30&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Hail radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/hailnl/?ext=png&l=2&hist=10&forc=1&step=0&w=550&h=512', '/tmp/HetWeer/00.png')
                elif type == _("Satellite"):
                    urllib.urlretrieve('https://image.buienradar.nl/2.0/image/sprite/SatVisual?height=512&width=550&history=12&skip=0', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Sunpower-UV"):
                    urllib.urlretrieve('https://image.buienradar.nl/2.0/image/sprite/WeatherMapUVIndexNL?extension=png&l=2&hist=0&forc=10&step=0&width=550&height=512', '/tmp/HetWeer/00.png')
                    legend = False
                if not type == _("Weather forecast-nl"):
                    openScreenRadar()

            elif state[0] == _("Europe") and newView:
                if type == _("Weather forecast-nl"):
                    wchat = weatherchat("nl/wereldwijd/europa")
                    self.session.open(weathertalk)
                elif type == _("Rainfall radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarmapeu/?ext=png&l=2&hist=0&forc=10&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Thunder radar"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/radarcloudseu/?ext=png&l=2&hist=8&forc=0&step=0&h=512&w=550', '/tmp/HetWeer/00.png')
                elif type == _("Satellite"):
                    urllib.urlretrieve('http://api.buienradar.nl/image/1.0/satvisual2/?ext=png&l=2&hist=10&forc=1&step=0&type=eu&w=550&h=512', '/tmp/HetWeer/00.png')
                    legend = False
                elif type == _("Sunpower-UV"):
                    urllib.urlretrieve('https://image.buienradar.nl/2.0/image/sprite/WeatherMapUVIndexNL?extension=png&l=2&hist=0&forc=10&step=0&width=550&height=512', '/tmp/HetWeer/00.png')
                    legend = False
                if not type == _("Weather forecast-nl"):
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
        except:
            self.session.open(MessageBox, _("Download error: Server disconnected while calling, try again later."), MessageBox.TYPE_INFO)
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
        self["key_red"] = Label(_("Exit"))

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
            if pos >= get_image_info('/tmp/HetWeer/00.png')[0] / (550):
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
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/blue34.png" position="1500,1032" size="34,34" alphatest="on"/>
            <widget name="key_blue" position="1550,1030" size="370,38" zPosition="3" transparent="1" font="Regular;36" borderColor="black" borderWidth="1" halign="left"/>
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
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/buttons/blue26.png" position="970,643" size="26,26" alphatest="on"/>
            <widget name="key_blue" position="1010,643" size="220,28" zPosition="3" transparent="1" font="Regular;24" borderColor="black" borderWidth="1" halign="left"/>
        </screen>"""

    def __init__(self, session):
        self.session = session
        self.skin = localcityscreen.skin
        self["favor"] = Label(_("Favorite Locations"))
        self["plaatsn"] = Label(_("Location:"))
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Location +"))
        self["key_yellow"] = Label(_("Location -"))
        self["key_blue"] = Label(_("Help"))
        Screen.__init__(self, session)
        list = []
        global SavedLokaleWeer
        for x in SavedLokaleWeer:
            list.append((str(x).split("-")[0]))
        self["list"] = MenuList(list)
        self["actions"] = ActionMap(["WizardActions"], {"ok": self.go, "back": self.close}, -1)
        self["ColorActions"] = HelpableActionMap(self, "ColorActions", {"red": self.exit, "yellow": self.removeLoc, "green": self.addLoc, "blue": self.addcityinf}, -1)

    def exit(self):
        self.close()

    def addLoc(self):
        self.session.openWithCallback(self.searchCity, VirtualKeyBoard, title=(_("Enter cityname e.g. london or london/gb or london_us")), text="")

    def addcityinf(self):
        self.session.open(MessageBox, _("Manual adding Citynumbers:\nGo to www.buienradar...\nSearch city and find citycode in internetlink.\n\nGo back to \"Location +\" and add cityname-number e.g.\n\"Dusseldorf-2934246\" or \"Dusseld-2934246\"\nDon't forget the \"-\" sign."), MessageBox.TYPE_INFO)

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
            try:
                if getLocWeer(SavedLokaleWeer[index].rstrip()):
                    time.sleep(1)
                    self.session.open(weeroverview)
                else:
                    self.session.open(MessageBox, _("Download error: Check spelling or ask to add the CityName to the database."), MessageBox.TYPE_INFO)
            except:
                self.session.open(MessageBox, _("Download error: No response try again"), MessageBox.TYPE_INFO)
                
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
        try:
            response = urllib2.urlopen("http://claudck193.193.axc.nl/wallpapers/daa.php?data")
            ids = int(response.read())
            with open('/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.txt', 'rb') as f:
                data = f.read()
            if not int(data) == ids:
                urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/backgroundhd.png')
                urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php?small', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.png')
	        urllib.urlretrieve('http://claudck193.193.axc.nl/wallpapers/daa.php?data', '/usr/lib/enigma2/python/Plugins/Extensions/HetWeer/Images/background.txt')
        except:
            None    
        session.open(startScreen)
        
    else:
        session.open(MessageBox, _("No Internet"), MessageBox.TYPE_INFO)

def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    return PluginDescriptor(name=_("TheWeather"), description=_("RainfallRadar & WeatherInfo") + versienummer,
                            icon="Images/weerinfo.png",
                            where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)