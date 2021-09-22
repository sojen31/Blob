#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
__authors__ = ("Jean-Pierre Coudray")
__contact__ = ("jeanpierrecoudray@gmail.com")
__version__ = "1.0.0"
__copyright__ = "copyleft"
__date__ = "2021/09/14"

##############################################################################################################################################
#################################################### EN ######################################################################################
##############################################################################################################################################
DESCRIPTION:
 ------------
 
Script taking a snapshot with the usb webcam (*) and placing it in the pathImage folder.
An info.csv file in the pathFile folder has one more line at each snapshot, with the date, image name and temperature data.
If the envoiMail variable is True then an email is sent at each snapshot with the image as an attached file (by gmail, you must therefore install yagmail and configure the MAIL informations)
(*) the webcam can be found with: v4l2-ctl --list-devices
   example: /dev/video0 to be used with fswebcam
   the command: v4l2-ctl -d /dev/video0 --list-ctrls
      allow to list the webcam controles
   the command: v4l2-ctl -d /dev/video0 --set-ctrl=focus_auto=0
      allow to desactivate the autofocus from the command line (use gucview for GUI)
  the command: v4l2-ctl -d /dev/video0 --set-ctrl=focus_absolute=40
      allow to specify a focal when autofocus is desactivet. Value is 40 here (use gucview for GUI)

PREREQUISITES:
 -----------
  -an usb webcam
 -a temperature sensor: ds18b20 whose ID has to be retrieved
 -yagmail module from python
 -fswebcam for images captures
 -imageMagick to check (command line) whether an image has a low light (and thus the lamp isn't working)
 -guvcview whether we want to desactivate the autofocus whith GUI (and not with command line)
 -pathImage and pathFile folders should exist

 USAGE:
 ------
 launch with crontab for a regular capture of images
 
 PARAMETEES:
 -----------
    None
	
 AMELIORATIONS:
 --------------
 
    
##############################################################################################################################################
#################################################### FR ######################################################################################
##############################################################################################################################################

 DESCRIPTION:
 ------------
 
Script prenant un cliche avec la webcam usb(*) et placement dans le dossier pathImage.
Un fichier info.csv dans le dossier pathFile a une ligne de plus a chaque cliche, avec comme donnees la date, le nom de l image et la temperature
Si la variable envoiMail est a True alors un courriel est envoye a chaque cliche avec l image en fichier joint (par gmail, il faut donc installer yagmail et parametrer la cartouche MAIL)

(*) la camera peut etre trouve avec la commande: v4l2-ctl --list-devices
   exemple: /dev/video0 a utiliser pour l utilitaire fswebcam
   la commande: v4l2-ctl -d /dev/video0 --list-ctrls
      permet de lister les controles possibles de la camera
   la commande v4l2-ctl -d /dev/video0 --set-ctrl=focus_auto=0
      permet de desactiver l autofocus en ligne de commande (utiliser gucview pour du GUI)
   la commande v4l2-ctl -d /dev/video0 --set-ctrl=focus_absolute=40
      permet de specifier une focale lorsque l autofocus est desactive. La valeur est ici 40 (utiliser gucview pour du GUI)

PREREQUIS:
 -----------
  -une webcam usb
 -une sonde de temperature ds18b20 dont l identifiant est a recuperer
 -le module yagmail de python
 -l utilitaire fswebcam pour les captures d images
 -l utilitaire imageMagick pour tester en ligne de commande si une image a une luminosite tres faible (et donc si la lampe ne fonctionne pas)
 -l utilitaire guvcview si on souhaite desactiver l autofocus via GUI et non en ligne de commmande
 -les dossiers pathImage et pathFile doivent etre crees

 USAGE:
 ------
 lancement via la crontab pour une capture reguliere d images
 
 PARAMETRES:
 -----------
    Aucun
	
 AMELIORATIONS:
 --------------
 
    
"""

from datetime import datetime
import time
import subprocess
import RPi.GPIO as GPIO
import yagmail


# GPIO use for the relay (switching the lamp)
#Utilisation de GPIO pour le relais (allumage de la lampe)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)



#######################################
#######################################
#          variables
#######################################
#######################################

pathImage = '/home/pi/Pictures/blob/images/'          # path to images storage   # chemin de stockage des images
pathFile = '/home/pi/Pictures/blob/files/'          # path to files storage as CSV (for snapchot informations)   #chemin de stockage des fichiers tel le CSV contenant les info de prises de vues
dateFormatee = datetime.now().isoformat(timespec='seconds')          # get the time stamping of snapshot   # obtention de l horodatage des prises de vues
pathWebcam = '/dev/video0'          # path to webcam hardware   #chemin vers le materiel de la webcam
idSondeTemp = '28-051780992cff'          # ID of temperature sensor ls /sys/bus/w1/devices/   # identifiant de la sonde de temperature ls /sys/bus/w1/devices/
temperature = '0'          # variable of reading temperature    # variable contenant la temperature relevee
envoiMailTF = False          # boolean indicating whether a mail will be sent at each image    # boolean indiquant si oui/non on envoie un courriel a chaque cliche
photoJointeAuMail = False          # boolean indicating whether the image will be attached with the mail    # boolean indiquant si oui/non on joint la photo au courriel
lampe = 6          # GPIO output to switch on the lamp via the relay    #  GPIO de sortie pour allumer la lampe via le relais


#######################################
#             MAIL VIA GMAIL

courrielExpediteur = ''    # sender email   #email de l expediteur
passExpediteur = '  '     #password    #mot de passe de l expediteur
courrielDestinataire = ''    # recipient email     #email du destinataire

#######################################

#######################################
#######################################
#######################################



# output GPIO to switch on the lamp
# GPIO en sortie pour allumer la lampe
GPIO.setup(lampe, GPIO.OUT)





# sending email function
# Fonction d envoi de courriel

def envoiMail(msg, avecPhoto):
   try:
      if avecPhoto: yagmail.SMTP(courrielExpediteur, passExpediteur).send(to= courrielDestinataire, subject= 'blob', contents= msg, attachments= pathImage + dateFormatee + '.jpg')
      else: yagmail.SMTP(courrielExpediteur, passExpediteur).send(to= courrielDestinataire, subject= 'blob', contents= msg)
   except:
      print('L envoi de courriel a echoue')








# Message to be sent: email test and simple print if ko
# Message a envoyer: test par courriel et si ko alors simple print

def messageToBeSent(msg, avecFichier):
   try:
      envoiMail(msg, avecFichier)
   except:
      print(msg)






# get the temperature from sensor function
# Fonctions pour recuperer la temperature a partir de la sonde

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(idSonde):
    device_file = '/sys/bus/w1/devices/' + idSonde + '/w1_slave'
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        """temp_f = temp_c * 9.0 / 5.0 + 32.0"""
        return temp_c
        
        



# get temperature
# Recuperation de la temperature

try:
   temperature = str(read_temp(idSondeTemp))
except:
   messageToBeSent('Erreur dans la recuperation de la temperature', False)






# switch on the lamp and sleep
# Allumage de la lampe et attente de Xs
GPIO.output(lampe, GPIO.HIGH)
time.sleep(10)






# get image and put it into pathImage folder
# Capture de l image et depot dans le dossier pathImage

commande = (
   "fswebcam " +
   "-d " + pathWebcam + " " +
   "-r 1280x720 " +
   "--info  Température:" + temperature + "°c. " +
   pathImage + dateFormatee + ".jpg")

try:
   subprocess.call(commande, shell=True)
except:
   messageToBeSent('Erreur dans le traitement de fswebcam', False)







# switch off th light
# Extinction de lampe

GPIO.output(lampe, GPIO.LOW)









# test whether the lamp is ok (sufficient brightness (upstream tested threshold)), otherwise warning email
# ImageMagick allow to get the value below witch we considere that  britghtness is nearly null
#      convert <image> -colorspace Gray -format "%[fx:quantumrange*image.mean]" info:
#
# Test si la lampe fonctionne (luminosite de l image au dela d un seuil teste en amont), sinon courriel d avertissement
# ImageMagick permet via la commande:
#     convert <image> -colorspace Gray -format "%[fx:quantumrange*image.mean]" info:
# d obtenir une valeur en deca de laquelle on considere que la luminosite est quasi nulle

commandeLuminosite = (
   'convert ' +
   pathImage + dateFormatee + '.jpg ' +
   '-colorspace Gray ' +
   '-format "%[fx:quantumrange*image.mean]" ' +
   'info:')

try:
   t = subprocess.check_output(commandeLuminosite, shell=True)
   t=t.decode('utf-8')
   if float(t) < 10000: envoiMail('La lampe semble ne pas fonctionner car la luminosite de l image est tres faible.', False)
except:
   messageToBeSent('Erreur dans le traitement de convert de imageMagick', False)







# informations concatenation into the CSV file
# concatenation des infos dans le fichier CSV

try:
   f=open(pathFile + "info.csv", "a+")
   f.write("%s %s %s \r\n" % (dateFormatee, temperature, dateFormatee + ".jpg"))
   f.close()
except:
   messageToBeSent('Erreur dans l ecriture du fichier info.csv', False)






# email sending
# Envoi de courriel

if envoiMailTF: envoiMail('nouvelle image du blob ' + dateFormatee, photoJointeAuMail)


