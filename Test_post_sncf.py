# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 18:03:47 2017

@author: NHNBYB
"""

#Sauvegardes

#demande='{"origin":"Paris (Toutes gares intramuros)","originCode":"FRPAR","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":"FRPAR","stationLabel":null},"destination":"Lille","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"2017-11-28T16:00:00","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":26,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'

#%%
import requests
import json
import pandas as pd
import numpy as np
import datetime

def calcul_anteriorite(date_rech,date2_python):
    annee=int(date_rech.split("-")[0])
    mois=int(date_rech.split("-")[1])
    jour=int(date_rech.split("-")[2])
    date_rech_format=datetime.datetime(annee,mois,jour)
    return  (date_rech_format-date2_python).days


headers = {
    'Host': 'www.voyages-sncf.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json;charset=utf-8',
    'X-VSD-SMART-GUY-GUARD': 'SdulvOlooN5;44534:T4QQRZD\\',
    'X-VSD-LOCALE':'fr_FR',
    'Referer': 'https://www.voyages-sncf.com/proposition?clientId=e8e421b8-2272-425e-a2cc-0016fc27c2da&language=fr&country=FR',
    'Content-Length': '1129',
    'Connection': 'keep-alive'
}


url='https://www.voyages-sncf.com/proposition/rest/search-travels/outward'

#Paramètres en entrée
villes_depart=['Paris']
villes_arrivee=['Lille','Lyon','Toulouse','Bordeaux','Marseille','Strasbourg','Brest','Rouen']
dates=['2017-11-28','2017-12-28']
horaires=['08:00:00','16:00:00']

##Pour faire un petit test, mini-échantillon
#villes_depart=['Paris']
#villes_arrivee=['Biarritz']
#dates=['2018-01-16']
#horaires=['08:00:00']

nb_obs=len(villes_depart)*len(villes_arrivee)*len(dates)*len(horaires)
tableau_result=pd.DataFrame(np.zeros(shape=(nb_obs,15)))
#Noms des colonnes
tableau_result.columns=["Départ rech","Arrivée rech","Date rech","Heure rech","Gare dép","Gare arriv","Horaire dép","Horaire arriv","Type","Prix noflex","Prix semiflex","Prix flex","Prop classe1","numero_train","antériorité"]

j=-1
for ville_depart in villes_depart:
    for ville_arrivee in villes_arrivee:
        for date in dates:
            for horaire in horaires:

                #On concatène pour avoir notre json de demande
                demande='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":26,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'

                #On effectue la requête
                r = requests.post(url, data=demande,headers=headers)

                #La requête a-t-elle fonctionné ? On veut 200
                print("Billet " + ville_depart + "-" + ville_arrivee + "   Statut : "+str(r))

                #Voici notre résultat ; il faut nettoyer la chaîne de caractères maintenant
                resultat=r.text
                resultat2=resultat.replace("\'","")
                resultat2=resultat2.replace('\\"','"')
                resultat2=resultat2.replace('"{','{')
                resultat2=resultat2.replace('}"','}')
                resultat2=resultat2.replace('//','')
                resultat2=resultat2.replace('="','')
                resultat2=resultat2.replace('">','')
                resultat2=resultat2.replace(';"','')

                #Conversion en json
                try:
                    resultat3=json.loads(resultat2)

                    nb_trains=len(resultat3["results"])
                    for n in range(nb_trains):

                        if len(resultat3["results"][n]["priceProposals"])>0: #Critère pour vérifier qu'il s'agit bien d'un train - à remplacer éventuellement
                            j=j+1

                            if j>0:
                                tableau_result.loc[j]=0
                            #On inscrit dans le tableau les paramètres d'entrée
                            tableau_result.iloc[j,0:4]=[ville_depart,ville_arrivee,date,horaire]

                            ##On inscrit dans le talbeau les résultats
                            #D'abord les villes de départ, arrivée, la date et les horaires effectifs :
                            tableau_result.iloc[j,4]=resultat3["results"][n]["origin"]
                            tableau_result.iloc[j,5]=resultat3["results"][n]["destination"]
                            tableau_result.iloc[j,6]=resultat3["results"][n]["departureDate"]
                            tableau_result.iloc[j,7]=resultat3["results"][n]["arrivalDate"]

                            #Le type de transport :
                            tableau_result.iloc[j,8]=resultat3["results"][n]["segments"][0]["transporter"]
                            nb_correspondances=len(resultat3["results"][n]["segments"])
                            i=0
                            while i+1<nb_correspondances:
                                i=i+1
                                tableau_result.iloc[j,8]=tableau_result.iloc[j,8]+" puis "+resultat3["results"][n]["segments"][i]["transporter"]

                            #Puis les prix !
                            try:
                                tableau_result.iloc[j,9]=resultat3["results"][n]["priceProposals"]["NOFLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.iloc[j,10]=resultat3["results"][n]["priceProposals"]["SEMIFLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.iloc[j,11]=resultat3["results"][n]["priceProposals"]["FLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.iloc[j,12]=resultat3["results"][n]["priceProposals"]["UPSELL"]["amount"]
                            except:
                                pass

                            #Enfin, le numéro du train et la classe d'antériorité
                            tableau_result.iloc[j,13]=resultat3["results"][n]["segments"][0]["trainNumber"]
                            tableau_result.iloc[j,14]=str(calcul_anteriorite(date,datetime.datetime.now()))+" jours"
                            print(" Réussi")

                except:
                    print(" Raté")
                    pass


#%%
#On exporte en csv
import datetime
date = datetime.datetime.now()
tableau_result.to_csv("SNCF_"+str(date.year)+str(date.month)+str(date.day)+"_"+"{:d}h{:02d}".format(date.hour, date.minute)+".csv")


#%%Pour copier quelque-chose dans le presse-papier

import pyperclip
pyperclip.copy(resultat2)


















