from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Pixmap import Pixmap
from twisted.web.client import downloadPage, getPage
from Screens.MessageBox import MessageBox
from enigma import ePicLoad, getDesktop, eTimer
from Components.AVSwitch import AVSwitch
import urllib2, urllib
import os
from Tools.Directories import resolveFilename, SCOPE_CONFIG, SCOPE_PLUGINS
from Screens.HelpMenu import HelpableScreen
from Components.FileList import FileList

labeltext = "=--Weer App--=\nMade by DEG & PD1LOI 2012~2015!"

def getScale():
	return AVSwitch().getFramebufferScale()

class Weermenu(Screen):
	skin = """
		<screen position="center,center" size="360,290" title="Het weer" >
			<widget name="list" position="10,0" size="350,190" scrollbarMode="showOnDemand" />
			<widget name="Text" position="center,190" size="360,100" halign="center" font="Regular;22" />
                </screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self["list"] = MenuList([])		
		self["Text"] = Label(labeltext)
		self["myActionMap"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.cancel}, -1)

		self.weer = []
		self.weer.append("Neerslag Radars")
		self.weer.append("Sat foto's")
		self.weer.append("Sat infrarood kaarten")
                self.weer.append("Temperatuur kaarten")
                self.weer.append("Waarschuwings kaarten")
		self.weer.append("Onweer kaarten")
		self.weer.append("Pluimgrafieken")
		self["list"].setList(self.weer)

	def cancel(self):
		self.close(None)

	def okClicked(self):
		i = self["list"].getSelectionIndex()
		j = self.weer[i]
		self.session.open(secondmenu, j)

class secondmenu(Screen):
	skin = """
		<screen position="center,center" size="800,510" title="Het weer" >
			<widget name="list" position="10,3" size="390,410" scrollbarMode="showOnDemand" />
			<widget name="Text" position="0,430" size="390,90" halign="center" font="Regular;22" />
			<widget name="Info" position="410,5" size="390,250" font="Regular;22" />
		</screen>"""

	def __init__(self, session, iweertext, ktekst = None ,urlpart1 = None):
		self.skin = secondmenu.skin
		Screen.__init__(self, session)
		self["list"] = MenuList([])
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"], {"ok": self.okClicked, "cancel": self.cancel,"up": self.key_up,"down": self.key_down,"left": self.key_left,"right": self.key_right}, -1)
		self.options = []
		self.wtext = []
		self.iweertext = iweertext
		self.urlp1 = urlpart1
		dir = "/tmp/HetWeer/"
		if not os.path.exists(dir):
			print 'Path doesnt exists! Make it.'
			os.makedirs(dir)
		if self.iweertext == 'pluim2':
			self["Text"] = Label(_("=--%s--=\nMade by DEG & PD1LOI 2012~2015!") %(ktekst))
		else:
			self["Text"] = Label(labeltext)
		self["Info"] = Label("")
		self.onLayoutFinish.append(self.lijst)

	def cancel(self):
		self.close(None)
		
	def key_up(self):
		self["list"].up()
		self.updatetext()
		
	def key_down(self):
		self["list"].down()
		self.updatetext()
		
	def key_left(self):
		self["list"].pageUp()
		self.updatetext()
		
	def key_right(self):
		self["list"].pageDown()
		self.updatetext()

	def updatetext(self):
		i = 0
		i = self["list"].getSelectionIndex()
		text = self.options[i]
		if len(text) != [2]:
			try:
				self["Info"].setText(text[2])
			except:
				return

	def lijst(self):
		if self.iweertext == 'Neerslag Radars':
			#neerslag radar
			self.options = []
			self.options.append((_("Buienradar NL"),"http://www.buienradar.nl",'Live buienradar waar regent het nu!'))
		        self.options.append((_("Motregenradar NL"),"http://www.buienradar.nl/motregenradar",'Live buienradar waar het motregent nu! (Beweegt soms)'))
			self.options.append((_("2 uur vooruit NL"),"http://www.buienradar.nl",'2 uur vooruit kijken of het dan nog regent'))
			self.options.append((_("Zomerradar NL"),"http://zomerradar.buienradar.nl",'Zomerradar waar schijnt de zon!\Gele kleur is zonnig gebied.'))
			self.options.append((_("Zomerradar Bewolking NL"),"http://zomerradar.buienradar.nl/wolken-afgelopen-uur",'Wolkenradar hier kun je de bewolking boven ons land zien.'))
			self.options.append((_("Zomerradar Temperatuur NL"),"http://zomerradar.buienradar.nl/temperatuur",'Temperatuur verloop in Nederland.'))
			self.options.append((_("Zomerradar Zonkracht NL"),"http://zomerradar.buienradar.nl/zonkracht-verwacht",'Waar schijnt de zon het sterkst!'))
			self.options.append((_("Radar Europa"),"http://sat24.com/?ir=true&ra=true&li=false",'Live radar voor west Europa, voor als je op de fiets naar Frankrijk wil.'))
			self.options.append((_("Sneeuw NL"),"http://www.onweer-online.nl/images/maps/sneeuwradar.gif",'Sneeuwt het in Nederland ja of nee!'))
			self.options.append((_("Buienradar Belgie"),"http://www.buienradar.be",'Live buienradar voor de Belgen.'))
			self.options.append((_("Buienradar Duitsland"),"http://www.niederschlagsradar.de",'Live buienradar voor de Duitsers.'))
			#self.options.append((_("Buienradar UK"),"http://www.meteoradar.co.uk/",'Bekijk de buien boven United Kingdom.'))
			self["list"].setList(self.options)

		elif self.iweertext == 'Temperatuur kaarten':
			#Temperatuur
			self.options = []
			self.options.append((_("Knmi Actuele temperatuur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=temperatuur.000001.png&extension=png",'knmi actuele temperatuur kaart. \n\nKaart is stilstaand.'))
			self.options.append((_("Maximum temperatuur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=temperatuurmax.000001.png&extension=png",'knmi maximum temperatuur kaart. \n\nKaart is stilstaand.'))
                        self.options.append((_("Minimum temperatuur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=temperatuurmin.000001.png&extension=png",'Knmi actuele minimum temperatuur kaart. \n\nKaart is stilstaand.'))
                        self.options.append((_("Actuele grond temperatuur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=temperatuurgrond.000001.png&extension=png",'Knmi actuele grond temperatuur kaart. \n\nKaart is stilstaand.'))
                        self.options.append((_("Actuele Wind"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=wind.000001.png&extension=png",'Knmi actuele wind kaart. \n\nKaart is stilstaand.'))
                        self.options.append((_("Maximum Wind"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=windmax.000001.png&extension=png",'Knmi maximum wind. \n\nKaart is stilstaand.'))
			self.options.append((_("Windsnelheid midden Nederland"),"http://www.buienradar.nl/weatherstation/gaugeimage?stationCode=6269&type=windspeed",'Windsnelheid in De Bilt. \n\nKaart is stilstaand.'))
			self.options.append((_("Windrichting midden Nederland"),"http://www.buienradar.nl/weatherstation/gaugeimage?stationCode=6260&type=wind",'Windrichting Midden Nederland. \n\nKaart is stilstaand.'))
			self.options.append((_("Straalstroom Europa"),"http://wxmaps.org/pix/euro5.00hr.png",'Actueel straalstroom in Europa. \n\nKaart is stilstaand.'))
			self.options.append((_("Luchtdruk midden Nederland"),"http://www.buienradar.nl/weatherstation/gaugeimage?stationCode=6260&type=airpressure",'Luchtdruk in De Bilt. \n\nKaart is stilstaand.'))
			self.options.append((_("Actuele Zicht"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=zicht.000001.png&extension=png",'Knmi actuele zicht kaart. \n\nKaart is stilstaand.'))
                        self.options.append((_("Neerslag afgelopen uur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=neerslaguur.000001.png&extension=png",'Knmi actuele neerslag van het afgelopen uur. \n\nKaart is stilstaand.'))
                        self.options.append((_("Neerslag afgelopen 24 uur"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=neerslag24uur.000001.png&extension=png",'Knmi actuele neerslag van het afgelopen 24 uur. \n\nKaart is stilstaand.'))
			self.options.append((_("Relative Luchtvochtigheid"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=luchtvochtigheid.000001.png&extension=png",'Luchtvochtigheid. \n\nKaart is stilstaand.'))
			self.options.append((_("Relative Luchtvochtigheid Wereldkaart"),"http://www.onweer-online.nl/images/maps/uwssec.gif",'Luchtvochtigheid wereldkaart. \n\nKaart is stilstaand.'))
			self.options.append((_("Zonuren in Nederland"),"http://www.buienradar.nl/image/?type=weathermap-large&fn=zonneschijn.000001.png&extension=png",'Knmi aantal zonuren in Nederland. \n\nKaart is stilstaand.'))
                        self.options.append((_("Actuele gevoelstemperatuur"),"http://www.buienradar.nl//image/?type=weathermap-large&fn=gevoelstemperatuur.000001.png&amp;extension=png",'Actuele gevoelstemperatuur kaart. \n\nKaart is stilstaand.'))
			self.options.append((_("Hoogste temperatuur Wereldkaart"),"http://www.onweer-online.nl/images/maps/tempwunderground.gif",'Actuele hoogste temperatuur kaart. \n\nKaart is stilstaand.'))
			self.options.append((_("Zeetemperatuur Noordelijk Halfrond"),"http://www7320.nrlssc.navy.mil/hycomARC/navo/arcticsstnowcast.gif",'Temperatuur van het zeewater. \n\nKaart is stilstaand.'))
			self.options.append((_("Zeetemperatuur Noordzee"),"http://www.onweer-online.nl/images/maps/zeetempknmi.png",'Temperatuur van het zeewater. \n\nKaart is stilstaand.'))
			self.options.append((_("Zeetemperatuur Europa"),"http://www.buienradar.nl/image/seatemperature?region=eu",'Kaart wordt niet elke dag vernieuwt,er worden maar 28 metingen per week verricht.. \n\nKaart is stilstaand.'))
			self.options.append((_("Uv Straling"),"http://www.buienradar.nl/image/other?type=uv",'Uv stralen grafiek. \n\nKaart is stilstaand.'))
			self.options.append((_("Weerplaza"),"http://www.onweer-online.nl/images/maps/weerplaza_temperatuu.png",'Temperatuur kaart van weerplaza. \n\nKaart is stilstaand.'))
			self.options.append((_("Weerplaza Weerbeeld"),"http://www.onweer-online.nl/images/maps/weerplaza_weerbeeld.jpg",'Actueel weerbeeld kaart van weerplaza. \n\nKaart is stilstaand.'))
                        self["list"].setList(self.options)
                        
                        
                elif self.iweertext == 'Waarschuwings kaarten':
			#waarschuwing
			self.options = []
                        self.options.append((_("Waarschuwingen in Nederland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_neder.png",'Waarschuwingen in Nederland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Kustdistricten"),"http://www.buienradar.nl/image/?type=weerwaarschuwing&fn=nederland-kust.png",'Waarschuwingen langs de kust. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Groningen"),"http://www.onweer-online.nl/images/maps/waarschuwingen_groni.png",'Waarschuwingen in Groningen. \n\nKaart is stilstaand.'))
	                self.options.append((_("Waarschuwingen in Friesland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_fries.png",'Waarschuwingen in Friesland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Drente"),"http://www.onweer-online.nl/images/maps/waarschuwingen_drent.png",'Waarschuwingen in Drente. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Overijsel"),"http://www.onweer-online.nl/images/maps/waarschuwingen_overi.png",'Waarschuwingen in Overijsel. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Gelderland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_gelde.png",'Waarschuwingen in Gelderland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Flevoland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_flevo.png",'Waarschuwingen in Flevoland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Utrecht"),"http://www.onweer-online.nl/images/maps/waarschuwingen_utrec.png",'Waarschuwingen in Utrecht. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in N Holland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_noord.png",'Waarschuwingen in N Holland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Z Holland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_zuid-.png",'Waarschuwingen in Z Holland. \n\nKaart is stilstaand.'))
	                self.options.append((_("Waarschuwingen in Zeeland"),"http://www.onweer-online.nl/images/maps/waarschuwingen_zeela.png",'Waarschuwingen in Zeeland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Noordbrabant"),"http://www.onweer-online.nl/images/maps/waarschuwingen_braba.png",'Waarschuwingen in Noordbrabant. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Limburg"),"http://www.onweer-online.nl/images/maps/waarschuwingen_limbu.png",'Waarschuwingen in Limburg. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Nederland Vandaag"),"http://www.onweer-online.nl/images/maps/knmi_vandaag.png",'Waarschuwingen in Nederland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Nederland Morgen"),"http://www.onweer-online.nl/images/maps/knmi_morgen.png",'Waarschuwingen in Nederland. \n\nKaart is stilstaand.'))
		        self.options.append((_("Waarschuwingen in Nederland Overmorgen"),"http://www.onweer-online.nl/images/maps/knmi_overmorgen.png",'Waarschuwingen in Nederland. \n\nKaart is stilstaand.'))
                        self.options.append((_("Estofex storm west Europa"),"http://www.onweer-online.nl/images/maps/estofex.png",'European Storm Forecast Experiment. \n\nKaart is stilstaand.'))
                        self["list"].setList(self.options)


		elif self.iweertext == 'Onweer kaarten':
			#Onweer
			self.options = []
			self.options.append((_("Bliksem.nu"),"http://www.onweer-online.nl/images/maps/Bliksem.nu.png",'Onweer kaart van bliksem.nu \n\nKaart is stilstaand.'))
			self.options.append((_("Station Woerden"),"http://www.onweer-online.nl/images/maps/weerstation_woerden.png",'Onweer kaart van weerstation Woerden \n\nKaart is stilstaand.'))
			self.options.append((_("Station Mechelen"),"http://www.onweer-online.nl/images/maps/weerstation_mechelen.png",'Onweer kaart van weerstation Mechelen \n\nKaart is stilstaand.'))
			self.options.append((_("Blitzortung"),"http://www.onweer-online.nl/images/maps/blitzortung.png",'Onweer kaart van Europa \n\nKaart is stilstaand.'))
			self.options.append((_("Station Lopik"),"http://www.onweer-online.nl/images/maps/doppler.jpg",'Onweer kaart van Lopik en omgeving. \n\nKaart is stilstaand.'))
                        self.options.append((_("Blids.de"),"http://www.onweer-online.nl/images/maps/blids.jpg",'Onweer kaart van bilds.de \n\nKaart is stilstaand.'))
			self["list"].setList(self.options)


		elif self.iweertext == 'Pluimgrafieken':
			#Pluimen
			self.options = []
			self.options.append((_("Noord"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL020",'Pluimgrafiek van Noord nederland'))
			self.options.append((_("Noord-West"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL015",'Pluimgrafiek van Noord-West nederland'))
			self.options.append((_("Noord-Oost"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL018",'Pluimgrafiek van Noord-Oost nederland'))
			self.options.append((_("Midden-West"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL011",'Pluimgrafiek van Midden-West nederland'))
			self.options.append((_("Midden"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL012",'Pluimgrafiek van Midden nederland'))
			self.options.append((_("Midden-Oost"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL009",'Pluimgrafiek van Midden-Oost nederland'))
			self.options.append((_("Zuid-West"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL002",'Pluimgrafiek van Zuid-West nederland'))
			self.options.append((_("Zuid"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL004",'Pluimgrafiek van Zuid nederland'))
			self.options.append((_("Zuid-Oost"),"http://grafiek.buienradar.nl/chart.ashx?w=1180&h=550&region=NL001",'Pluimgrafiek van Zuid-Oost nederland'))
			self["list"].setList(self.options)

		elif self.iweertext == 'pluim2':
			#Pluimen
			self.options = []
			self.options.append((_("Neerslag"),"&ecmwftype=13011&ctype=3"))
			self.options.append((_("Temperatuur"),"&ecmwftype=12004&ctype=3"))
			self.options.append((_("Dauwpunt"),"&ecmwftype=12006&ctype=3"))
			self.options.append((_("Windrichting"),"&ecmwftype=11011&ctype=3"))
			self.options.append((_("Windsnelheid"),"&ecmwftype=11012&ctype=3"))
			self.options.append((_("Windstoten"),"&ecmwftype=11041&ctype=3"))
			self.options.append((_("Sneeuw/hagel/ijs neerslag"),"&ecmwftype=13233&ctype=3"))
			self.options.append((_("Bewolking"),"&ecmwftype=20010&ctype=3"))
			self["list"].setList(self.options)

		elif self.iweertext == "Sat foto's":
			#Pluimen
			self.options = []
			self.options.append((_("Benelux"),"http://sat24.com/nl/nl"))
			self.options.append((_("Europa"),"http://sat24.com/nl/eu"))
			self.options.append((_("De alpen"),"http://sat24.com/nl/alps"))
			self.options.append((_("Duitsland"),"http://sat24.com/nl/de"))
			self.options.append((_("Groot Brittanie"),"http://sat24.com/nl/gb"))
			self.options.append((_("Afrika"),"http://sat24.com/nl/af"))
			self.options.append((_("Italie"),"http://sat24.com/nl/it"))
                        self.options.append((_("Turkye"),"http://sat24.com/nl/tu"))
                        self.options.append((_("Zuid Oost Europa"),"http://sat24.com/nl/se"))
                        self.options.append((_("Rusland"),"http://sat24.com/nl/ru"))
                        self.options.append((_("Griekenland"),"http://sat24.com/nl/gr"))
                        self.options.append((_("Baltische Staten"),"http://sat24.com/nl/bc"))
                        self.options.append((_("Scandinavie"),"http://sat24.com/nl/scan"))
                        self.options.append((_("Spanje en Portugal"),"http://sat24.com/nl/sp"))
			self.options.append((_("Frankrijk"),"http://sat24.com/nl/fr"))
			self.options.append((_("Canarische Eilanden"),"http://sat24.com/nl/ce"))
                        self.options.append((_("Zuid Afrika"),"http://sat24.com/nl/za"))
                        self["list"].setList(self.options)
			
		elif self.iweertext == "Sat infrarood kaarten":
			#Pluimen
			self.options = []
			self.options.append((_("Benelux"),"http://sat24.com/nl/nl?ir=true"))
			self.options.append((_("Europa"),"http://sat24.com/nl/eu?ir=true"))
			self.options.append((_("De alpen"),"http://sat24.com/nl/alps?ir=true"))
			self.options.append((_("Duitsland"),"http://sat24.com/nl/de?ir=true"))
			self.options.append((_("Groot Brittanie"),"http://sat24.com/nl/gb?ir=true"))
			self.options.append((_("Afrika"),"http://sat24.com/nl/af?ir=true"))
                        self.options.append((_("Italie"),"http://sat24.com/nl/it?ir=true"))
                        self.options.append((_("Turkye"),"http://sat24.com/nl/tu?ir=true"))
                        self.options.append((_("Zuid Oost Europa"),"http://sat24.com/nl/se?ir=true"))
                        self.options.append((_("Rusland"),"http://sat24.com/nl/ru?ir=true"))
                        self.options.append((_("Griekenland"),"http://sat24.com/nl/gr?ir=true"))
                        self.options.append((_("Baltische Staten"),"http://sat24.com/nl/bc?ir=true"))
                        self.options.append((_("Scandinavie"),"http://sat24.com/nl/scan?ir=true"))
			self.options.append((_("Spanje en Portugal"),"http://sat24.com/nl/sp?ir=true"))
			self.options.append((_("Frankrijk"),"http://sat24.com/nl/fr?ir=true"))
                        self.options.append((_("Canarische Eilanden"),"http://sat24.com/nl/ce?ir=true"))
                        self.options.append((_("Zuid Afrika"),"http://sat24.com/nl/za?ir=true"))
			self["list"].setList(self.options)
		
		self.updatetext()

	def okClicked(self):
		ioptie = self["list"].getSelectionIndex()
		option = self.options[ioptie]
		print option
		self.keuzetekst = option[0]
		iweeroption = option[1]
		print self.keuzetekst
		self.url = iweeroption
		try:
			if self.iweertext == 'Pluimgrafieken':
				self.urlpart1 = iweeroption
				self.session.open(secondmenu, 'pluim2', self.keuzetekst, self.urlpart1)
			elif self.iweertext == 'pluim2':
				url = self.urlp1 + self.url
				downloadPage(url,"/tmp/HetWeer.png").addCallback(self.downloadDone).addErrback(self.downloadError)
			elif self.iweertext == 'Neerslag Radars':
				if self.keuzetekst == "Buienradar NL":
					getPage(self.url).addCallback(self.done,'/actueel','nl').addErrback(self.downloadError)
				elif self.keuzetekst == "Motregenradar NL":
					getPage(self.url).addCallback(self.done,'/motregenradar','nl', 'shuffle').addErrback(self.downloadError)	
				elif self.keuzetekst == "Zomerradar NL":
					getPage(self.url).addCallback(self.done,'/zon','nl', 'shuffle').addErrback(self.downloadError)
				elif self.keuzetekst == "Zomerradar Bewolking NL":
					getPage(self.url).addCallback(self.done,'/wolken','nl', 'shuffle').addErrback(self.downloadError)
				elif self.keuzetekst == "Zomerradar Temperatuur NL":
					getPage(self.url).addCallback(self.done,'/temperatuur','nl', 'shuffle').addErrback(self.downloadError)
				elif self.keuzetekst == "2 uur vooruit NL":
					getPage(self.url).addCallback(self.done,'/radar-verwachting','nl', 'shuffle').addErrback(self.downloadError)
				elif self.keuzetekst == "OnweerRadar Europa":
					getPage(self.url).addCallback(self.Sat24done).addErrback(self.downloadError)
				elif self.keuzetekst == "Radar Europa":
					getPage(self.url).addCallback(self.Sat24done).addErrback(self.downloadError)
				elif self.keuzetekst == "Buienradar Belgie":
					getPage(self.url).addCallback(self.done,'/radar','be').addErrback(self.downloadError)
				elif self.keuzetekst == "Buienradar Duitsland":
					getPage(self.url).addCallback(self.done,'srt=bild','de').addErrback(self.downloadError)
				elif self.keuzetekst == "3 Dagen vooruit Eu":
					getPage(self.url).addCallback(self.BR3Ddone).addErrback(self.downloadError)
				elif self.keuzetekst == "Zomerradar Zonkracht NL":
					getPage(self.url).addCallback(self.ZONdone).addErrback(self.downloadError)
				elif self.keuzetekst == "Buienradar UK":
					getPage(self.url).addCallback(self.done,'type=rain','uk').addErrback(self.downloadError)
				else:
					downloadPage(self.url,"/tmp/HetWeer.png").addCallback(self.downloadDone).addErrback(self.downloadError)
			elif self.iweertext == "Sat foto's":
				getPage(self.url).addCallback(self.Sat24done).addErrback(self.downloadError)
			elif self.iweertext == "Sat infrarood kaarten":
				getPage(self.url).addCallback(self.Sat24done).addErrback(self.downloadError)
			else:
				downloadPage(self.url,"/tmp/HetWeer.png").addCallback(self.downloadDone).addErrback(self.downloadError)
		except:
			return

	def downloadError(self, raw):
		print "[e2Fetcher.fetchPage]: download Error", raw
		try:
			self.session.open(MessageBox, text = _("Error downloading"), type = MessageBox.TYPE_ERROR)
		except:
			return

	def downloadDone(self,raw):
		self.session.open(PictureScreen)


#handle the url:

	def done(self, raw, Type = None, url = None, shuffle = None):
		print 'here we go to get the pics'
		i = 1
		j = 0
		k2 = 0
				
		if url == 'nl':
			u2 = '<div class="time-list"><ul class="time-list-cols">'
		elif url == 'be':
			u2 = '<div class="time-list"><ul class="time-list-cols">'
		elif url == 'de':
			u2 = 'id="time-urls"'
		elif url == 'eu':
			u2 = '<div class="time-list"><ul class="time-list-cols">'
		elif url == 'uk':
			u2 = '<table id="time-urls" cellpadding="0" cellspacing="0">'
		else:
			return

		if u2 in raw:
			raw = raw.split(u2)
			print 'split done'
		
		k = 1
		c = raw[k]
		while not Type in c:
			c = raw[k]
			if Type not in c:
				k = k + 1	
		raw = raw[k]
		c = []
			
		if url == 'nl':
			u2 = '</div>'
			if u2 in raw:
				raw = raw.split(u2)[0]
		elif url == 'be':
			u2 = '</div>'
			if u2 in raw:
				raw = raw.split(u2)[0]
		elif url == 'de':
			u2 = '</table>'
			if u2 in raw:
				raw = raw.split(u2)[0]
		elif url == 'eu':
			u2 = '</div>'
			if u2 in raw:
				raw = raw.split(u2)[0]
		elif url == 'uk':
			u2 = '</table>'
			if u2 in raw:
				raw = raw.split(u2)[0]
				
		k2 = raw.count('href=')

		if raw.find('class="more"') or raw.find('meer') or raw.find('mehr'):
			print 'more found'
			k2 = k2 - 1
		
		raw = raw.split('href="')
		
		print k2
		print 'Thats the number of pictures we gonna show'
		
		while i<k2:
			href = raw[i]
			
			href = href.split('"')[0]
			print href
			k3 = href.count('/')
			if k3>0:
				href = href.split('/')[k3]
			if url != 'uk':
				k3 = 0
				k3 = href.count('time=')
				if k3>0:
					href = href.split('time=')[k3]
			k3 = 0
			k3 = href.count('h.aspx?')
			if k3>0:
				href = href.split('h.aspx?')[k3]

			if url == 'nl':
				print 'nl'
				#checknumber = isinstance(float(href), (int, long, float, complex))
				#if not checknumber:
				#	print 'geen nummer'
				#	break
				if Type == '/actueel':
					iurl = "http://www.buienradar.nl/image/?time=" + href + "&type=lightning&extension=png"
				elif Type == '/motregenradar':
					iurl = "http://www.buienradar.nl/image?type=motregen&amp;index=" + href	
				elif Type == '/zon':
					iurl = "http://zomerradar.buienradar.nl/image/zon/" + href
				elif Type == '/wolken':
					iurl = "http://zomerradar.buienradar.nl/image/wolken/" + href
				elif Type == '/temperatuur':
					iurl = "http://zomerradar.buienradar.nl/image/temperatuur/" + href
				elif Type == '/radar-verwachting':
					iurl = "http://www.buienradar.nl/image/?time=" + href + "&extension=png"
					iurl = iurl.replace('?type','&type')
					print 'new url'
				else:
					break
			elif url == 'be':
				checknumber = isinstance(float(href), (int, long, float, complex))
				if not checknumber:
					print 'geen nummer'
					break
				if Type == '/radar':
					iurl = "http://www.buienradar.be/image/?time=" + href
				else:
					break
			elif url == 'de':
				checknumber = isinstance(float(href), (int, long, float, complex))
				if not checknumber:
					print 'geen nummer'
					break
				iurl = "http://www.niederschlagsradar.de/image.ashx?type=bild&jaar=&regio=homepage&tijdid=" + href + "&time=" + href + "&bliksem=1"
			elif url == 'eu':
				iurl = "http://europa.buienradar.nl/images.aspx?" + href
			elif url == 'uk':
				href = href.replace('Home','')
				iurl = "http://www.meteoradar.co.uk/Content/image.ashx" + href
			else:
				break
			print iurl

			if shuffle == 'shuffle':
				if j>9:
					png = "/tmp/HetWeer/B%s.png" % j
				else:
					png = "/tmp/HetWeer/B0%s.png" % j
			else:
				if j>9:
					png = "/tmp/HetWeer/%s.png" % j
				else:
					png = "/tmp/HetWeer/0%s.png" % j

			print png
			try:
				urllib.urlretrieve(iurl, png)
			except:
				break

			j=j+1
			i=i+1

	#do we need shuffle time?
		if shuffle == 'shuffle':
			print "shuffle time"
			last=j-1
			j = 0
			print last
			while last>-1:


				if j>9:
					png = "/tmp/HetWeer/%s.png" % j
				else:
					png = "/tmp/HetWeer/0%s.png" % j


				if last>9:
					before = "/tmp/HetWeer/B%s.png" % last
				else:
					before = "/tmp/HetWeer/B0%s.png" % last


				try:
					os.rename(before, png)
				except:
					break


				last = last-1
				j=j+1

		if os.path.exists('/tmp/HetWeer/00.png'):
			try:
				self.session.open(View_Slideshow, j)
			except:
				return
		else:
			print '00.png doenst exists, go back!'
			return

#end of handle url!

	def BR3Ddone(self,raw):
		i = 0
		j = 0

		raw = raw.split('var imageBaseUrl')[1].split('</script>')[0]
		maxc = int(raw.split('var maxIndex = ')[1].split(';')[0])
		raw = raw.split("= '")[1].split("';")[0]
		
		while i<maxc:
			#http://europa.buienradar.nl/image/longtermforecast?type=neerslag&index=15
			iurl = raw.replace("&amp;",'&')
			iurl = iurl.replace("'+'{index}",'')
			iurl = iurl+str(i)
			iurl = 'http://europa.buienradar.nl'+iurl
			print iurl

			if j>9:
				png = "/tmp/HetWeer/B%s.png" % j
			else:
				png = "/tmp/HetWeer/B0%s.png" % j
			print png
			try:
				urllib.urlretrieve(iurl, png)
			except:
				break
			
			j=j+1
			i=i+1

		print "shuffle time"
		last=j-1
		j = 0
		print last
		while last>-1:


			if j>9:
				png = "/tmp/HetWeer/%s.png" % j
			else:
				png = "/tmp/HetWeer/0%s.png" % j


			if last>9:
				before = "/tmp/HetWeer/B%s.png" % last
			else:
				before = "/tmp/HetWeer/B0%s.png" % last


			try:
				os.rename(before, png)
			except:
				break


			last = last-1
			j=j+1

		if os.path.exists('/tmp/HetWeer/00.png'):
			try:
				self.session.open(View_Slideshow, j)
			except:
				return
		else:
			print '00.png doenst exists, go back!'
			return

	def Sat24done(self,raw):
		i = 0
		j = 0
		iurl = " "
		shuffle = None
		
		raw = raw.split('var maxcount = ')[1]
		maxcount = raw.split(';')[0]
		raw = raw.split('var imageUrls = ')[1].split(';')[0]
		raw = raw.replace('[','').replace(']','')
		raw = raw.split(',')
		
		maxcount = int(maxcount)
		while i<maxcount:
			iurl = raw[i]
			iurl = iurl.replace('"','')
			iurl = "http://www.sat24.com" + iurl
			print iurl
			
			if j>9:
				png = "/tmp/HetWeer/%s.png" % j
			else:
				png = "/tmp/HetWeer/0%s.png" % j
			print png
			try:
				urllib.urlretrieve(iurl, png)
			except:
				break

			j=j+1
			i=i+1

		if os.path.exists('/tmp/HetWeer/00.png'):
			try:
				self.session.open(View_Slideshow, j)
			except:
				return
		else:
			print '00.png doenst exists, go back!'
			return
                       	

	def ZONdone(self, raw):
		print 'here we go to get the pics'
		j = 0
		shuffle = 'shuffle'
		index = 0
		i = 0
		maxindex = 2
		u2 = 'src="/image/zonkracht?index={index}"'
                     
		
			
		n1 = raw.find(u2)
		if n1>0:
			raw = raw.split(u2)[1]
			print 'split done'
		
		n1 = raw.find('var index = ')
		if n1>0:
			index = raw.split('var index = ')[1].split(';')[0]
			print type(index)
		
		n1 = raw.find('var maxindex = ')
		if n1>0:
			maxindex = raw.split('var maxindex = ')[1].split(';')[0]
			print type(maxindex)
			
		n1 = raw.find('var imageurlformat = "')
		if n1>0:
			imageurlformat = raw.split('var imageurlformat = "')[1].split('{index}";')[0]
			print imageurlformat

		i = int(index)
		maxindex = int(maxindex)
		
		print maxindex
		print i
		while i<maxindex:
			
			print 'start'
			index = str(i)
			print index
			iurl = "http://zomerradar.buienradar.nl" + imageurlformat + index
			
			print iurl

			if shuffle == 'shuffle':
				if j>9:
					png = "/tmp/HetWeer/B%s.png" % j
				else:
					png = "/tmp/HetWeer/B0%s.png" % j
			else:
				if j>9:
					png = "/tmp/HetWeer/%s.png" % j
				else:
					png = "/tmp/HetWeer/0%s.png" % j

			print png
			try:
				urllib.urlretrieve(iurl, png)
			except:
				break

			j=j+1
			i = i + 1

	#do we need shuffle time?
		if shuffle == 'shuffle':
			print "shuffle time"
			last=j-1
			j = 0
			print last
			while last>-1:
				if j>9:
					png = "/tmp/HetWeer/%s.png" % j
				else:
					png = "/tmp/HetWeer/0%s.png" % j
				if last>9:
					before = "/tmp/HetWeer/B%s.png" % last
				else:
					before = "/tmp/HetWeer/B0%s.png" % last
				try:
					os.rename(before, png)
				except:
					break
				last = last-1
				j=j+1
		if os.path.exists('/tmp/HetWeer/00.png'):
			try:
				self.session.open(View_Slideshow, j)
			except:
				return
		else:
			print '00.png doenst exists, go back!'
			return

#end of handle url!




#show picture:


class PictureScreen(Screen):
	sz_w = getDesktop(0).size().width()
	sz_h = getDesktop(0).size().height()


	skin="""
		<screen name="Na Regen Komt Zonneschijn" position="center,center" size="%d,%d" title="Picture Screen" backgroundColor="noTransBG" scrollbarMode="showOnDemand" >
			<widget name="myPic" position="center,center" size="%d,%d" zPosition="1" alphatest="on" scrollbarMode="showOnDemand" />
		</screen>"""%( sz_w, sz_h, (sz_w - 75), (sz_h - 70) )


	def __init__(self, session):
		Screen.__init__(self, session)
		print "[PictureScreen] __init__\n"
		self.picPath = "/tmp/HetWeer.png"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["myPic"] = Pixmap()
		self["myActionMap"] = ActionMap(["SetupActions"],
			{
				"ok": self.cancel,
				"cancel": self.cancel
			}, -1)
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)


	def ShowPicture(self):
		if self.picPath is not None:
			self.PicLoad.setPara([
					self["myPic"].instance.size().width(),
					self["myPic"].instance.size().height(),
					self.Scale[0],
					self.Scale[1],
					0,
					1,
			"#002C2C39"])
			self.PicLoad.startDecode(self.picPath)


	def DecodePicture(self, PicInfo = ""):
		if self.picPath is not None:
			ptr = self.PicLoad.getData()
			self["myPic"].instance.setPixmap(ptr)


	def cancel(self):
		print "[PictureScreen] - cancel\n"
		try:
			pngfile = '/tmp/HetWeer.png'
			os.remove(pngfile)
		except:
			pass
		self.close(None)






##########################






#------------------------------------------------------------------------------------------
#---------------------- class InfoBarAspectSelection --------------------------------------
#------------------------------------------------------------------------------------------


class InfoBarAspectSelection:
	STATE_HIDDEN = 0
	STATE_ASPECT = 1
	STATE_RESOLUTION = 2
	def __init__(self):
		self["AspectSelectionAction"] = HelpableActionMap(self, "InfobarAspectSelectionActions",
			{
				"aspectSelection": (self.ExGreen_toggleGreen, _("Aspect list...")),
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
		keys = ["green", "",  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ]
		self.session.openWithCallback(self.aspectSelected, ChoiceBox, title=_("Please select an aspect ratio..."), list = tlist, selection = selection, keys = keys)


	def aspectSelected(self, aspect):
		if not aspect is None:
			if isinstance(aspect[1], str):
				if aspect[1] == "resolution":
					self.ExGreen_toggleGreen()
				else:
					open("/proc/stb/video/policy", "w").write(aspect[1])
					self.ExGreen_doHide()
		return		
#----------
# player pics


class View_Slideshow(Screen, InfoBarAspectSelection):


	def __init__(self, session, pindex, startslide=True):


		#pindex = 0 
		print "SlideShow is running ......."
		self.textcolor = "#ffffff"
		self.bgcolor = "#000000"
		space = 35
		size_w = getDesktop(0).size().width()
		size_h = getDesktop(0).size().height()


		self.skindir = "/tmp"
		self.skin = "<screen name=\"Na Regen Komt Zonneschijn\" position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" > \
			<eLabel position=\"0,0\" zPosition=\"0\" size=\""+ str(size_w) + "," + str(size_h) + "\" backgroundColor=\""+ self.bgcolor +"\" /> \
			<widget name=\"pic\" position=\"" + str(space) + "," + str(space) + "\" size=\"" + str(size_w-(space*2)) + "," + str(size_h-(space*2)) + "\" zPosition=\"1\" alphatest=\"on\" /> \
			<widget name=\"file\" position=\""+ str(space+45) + "," + str(space+10) + "\" size=\""+ str(size_w-(space*2)-50) + ",25\" font=\"Regular;20\" halign=\"left\" foregroundColor=\"" + self.textcolor + "\" zPosition=\"2\" noWrap=\"1\" transparent=\"1\" /> \
			</screen>"
		Screen.__init__(self, session)


		InfoBarAspectSelection.__init__(self)
		self["actions"] = ActionMap(["OkCancelActions", "MediaPlayerActions", "DirectionActions", "MovieSelectionActions"],
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
		self["file"] = Label(_("Please wait, photo is being loaded ..."))
		self.old_index = 0
		self.picfilelist = []
		self.lastindex = pindex - 1
		self.currPic = []
		self.shownow = True
		self.dirlistcount = 0
		#speed to play! (self.speed*100)
		self.speed = 8


		devicepath = "/tmp/HetWeer/"
		currDir = devicepath
		self.filelist = FileList(currDir, showDirectories = False, matchingPattern = "^.*\.(png)", useServiceRef = False)


		for x in self.filelist.getFileList():
			if x[0][1] == False:
				try:
					self.picfilelist.append(currDir + x[0][0])
				except:
					break
			else:
				self.dirlistcount += 1


		self.maxentry = pindex - 1
		#len(self.picfilelist)-1
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
		self.picload.setPara([self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], 0, int(0), self.bgcolor])
		if False == False:
			self["file"].hide()
		self.start_decode()


	def ShowPicture(self):
		if self.shownow and len(self.currPic):
			self.shownow = False
			self["file"].setText(self.currPic[0].replace(".png",""))
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
				text = picInfo.split('\n',1)
				text = "(" + str(self.pindex+1) + "/" + str(self.maxentry+1) + ") " + text[0].split('/')[-1]
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
		if True==False and self.lastindex == self.maxentry:
			self.PlayPause()
		self.shownow = True
		self.ShowPicture()


	def PlayPause(self):
		if self.slideTimer.isActive():
			self.slideTimer.stop()
		else:
			self.slideTimer.start(self.speed*100)
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
		#del self.picload
		#for file in self.picfilelist:
		#	print 'filelist ', file
		#	try:
		#		if debug: print pluginPrintname, file
		#		os.unlink(file)
		##	except:
		#		pass
		try:
			self.removedir = '/tmp/HetWeer/'
			#self.png = '.png'
			start = 0
			print 'max files: ', self.maxentry
			print 'delete files used'
			if self.maxentry < 10:
				while start < (self.maxentry + 1):
					pngfile = '/tmp/HetWeer/0' + str(start) + '.png'
					os.remove(pngfile)
					start += 1


			elif self.maxentry > 9:
				while start < (self.maxentry + 1):
					if start < 10:
						pngfile = '/tmp/HetWeer/0' + str(start) + '.png'
						os.remove(pngfile)
						start += 1
					else:
						pngfile = '/tmp/HetWeer/' + str(start) + '.png'
						os.remove(pngfile)
						start += 1


			print "unlink done"
		except:
			print "ah damn, no files deleted"
			pass


		self.close()






#-- main:


def main(session, **kwargs):
	session.open(Weermenu)


def Plugins(**kwargs):
	return PluginDescriptor(name=_("Het Weer"), description=_("Weer Informatie"), icon="plugin.png", where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], fnc=main)

 

	
