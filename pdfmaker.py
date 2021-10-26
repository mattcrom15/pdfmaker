### Convert to PDF Python Script

import anchorpoint as ap
import apsync as aps
from distutils.dir_util import copy_tree
from shutil import copy

from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickWindow
from PySide2.QtCore import QUrl, QObject, QMetaObject, Slot
from PySide2.QtQml import QQmlComponent

from fpdf import FPDF
import os
import datetime
from PIL import Image 

print("hello world")

# Anchorpoint UI class allows us to show e.g. Toast messages in Anchorpoint
ui = ap.UI()

# The Anchorpoint context object provides the predefined variables and the inputs from the YAML file.
apcontext = ap.Context.instance()
filePath = apcontext.absolutePath
yaml = apcontext.yamlDir

api = apcontext.createApi()

#pdf creation 
text_font = 'Helvetica'
bold_font = 'Helvetica-Bold'

logoPath =  yaml + "/__logo.png"
print(logoPath)

#gets current date and time
dt = datetime.datetime.today()
date = str(dt.day) + '/'+ str(dt.month) +'/' + str(dt.year)

#filename
''''''
class PDF(FPDF):
    def HeaderPage(self,logo,title,subtitle):
       '''logo (str): filepath to your logo, 
       title(str): title of the pdf, 
       subtitle(str): subtitle of pdf'''
       self.add_page("L")
       self.set_margin(0)
    #    title
       self.set_fill_color(20,22,26)
       self.set_font("Helvetica","",24)
       self.set_text_color(200)
       self.cell(w=self.epw + 150, h=self.eph,txt=title,border=0, fill=True,ln=1)
    #    Subtitle
       self.set_font("Helvetica","",16)
       self.set_text_color(130)
       if subtitle != "":
            self.cell(-self.epw / 1.2,-self.eph/1.1,subtitle,fill=False,border=0)
    #    logo
       img = Image.open(logo)
       self.image(img,self.w - 50,self.h-50,img.size[0]/11, img.size[1]/11)
       img.close()

def create_page(pdf,image,logo,logoPath):
   '''creates a page in the pdf,
   pdf(object): add instance of PDF Object, 
   image(str): image to add to page,
   logo(str): path to logo
   '''
   pdf.add_page("L")
   i= Image.open(image)
   pdf.image(i,0,0,w=pdf.epw,h=pdf.eph)
   if logo == True:
      img = Image.open(logoPath)
      pdf.image(img,pdf.w - 40,pdf.h-40,img.size[0]/15, img.size[1]/15)
      img.close()
   i.close()



# creates input ui 
class Controller(QObject):    
    @Slot(str,str)
    def create(self,pdfname,subtitle):
        pdf = PDF()
        pdf.HeaderPage(logoPath,pdfname,subtitle)
        x = 0
        for image in os.listdir(filePath):
            print(str(x) + " pages complete")
            create_page(pdf,filePath + "/" + image,False,logoPath)
            x= x+1
        pdf.output(filePath + "/" + pdfname + ".pdf")
        ui.showToast(pdfname + ".pdf created.")
        pass


#################################################################################################
# Everything from here is boilerplate that will be moved inside Anchorpoint provided libraries. #
#################################################################################################

# First, we check if we can access the Anchorpoint provided QApplication instance 
app = QApplication.instance()
if app is None:
    # Ouch, no Anchorpoint QApplication instance, this is not good. 
    # We show a toast in Anchorpoint and exit the script
    import sys
    ui.showToast("PySide2 hiccup", \
        ap.UI.ToastType.Info, \
        description="QApplication could not be accessed, please report a bug.")
    sys.exit()

# Instantiate our handy controller object
controller = Controller()

# Everything OK, we can access the active QML Engine from the Anchorpoint UI.
engine = ui.getQmlEngine()
if engine is None:
    ui.showToast("PySide2 hiccup", \
    ap.UI.ToastType.Info, \
    description="No QQmlApplicationEngine found, please report a bug.")
    exit()

# The QML context object used by Anchorpoint.
engineContext = engine.rootContext()

# The Anchorpoint root QQuickWindow
window = engine.rootObjects()[0]

# Load our QML file from the yaml directory.
component = QQmlComponent(engine, QUrl.fromLocalFile(f"{apcontext.yamlDir}/dialog.qml"))
if (component.status() is not QQmlComponent.Ready):
    # QML parsing error, see ap.log 
    print(f"QML errors: {component.errors()}", flush=True)
    ui.showToast("QML error", \
        ap.UI.ToastType.Fail, \
        description="QML file has errors. See ap.log for details.")
    exit()
    
# When creating the QML object from our QML file, we have to provide initial properties.
# First, we provide the parent object (the main window) so that Anchorpoint knows where to 
# show our QML dialog. 
# Second, we pass our controller object so that QML can call our python script again.
initialProperties = {"parent": window.contentItem(), "controller": controller}
qmlObject = component.createWithInitialProperties(initialProperties, engineContext)

# Tell the controller object about our QML object as well.
controller.qmlObject = qmlObject

# It is essential to parent our QMLComponent instance to the controller so that
# the instance is destroyed when the controller cleanup slot is called from QML.
qmlObject.setParent(controller) 

# Last but not least we have to call the "openDialog" QML method that brings up our fancy dialog.
QMetaObject.invokeMethod(qmlObject, "openDialog")