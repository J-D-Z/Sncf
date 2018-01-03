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
from dateutil.relativedelta import relativedelta

def calcul_anteriorite(date_rech,date2_python):
    annee=int(date_rech.split("-")[0])
    mois=int(date_rech.split("-")[1])
    jour=int(date_rech.split("-")[2])
    date_rech_format=datetime.datetime(annee,mois,jour)
    return  (date_rech_format-date2_python).days+1

def nettoyage(reponse):
    res=reponse.replace("\'","")
    res=res.replace('\\"','"')
    res=res.replace('"{','{')
    res=res.replace('}"','}')
    res=res.replace('//','')
    res=res.replace('="','')
    res=res.replace('">','')
    res=res.replace(';"','')
    return res

def remplir(tableau_donnees,json_file,cols,champs,nb_trains):
    tab=pd.DataFrame([])
    tab["numéro train"]=0
    for i in range(len(cols)):
        c=cols[i]
        tab[c]=0
    j=-1
    try:
        res=json.loads(json_file)
        nb_tr=len(resultat3["results"])
        for n in range(nb_tr):
            if len(resultat3["results"][n]["priceProposals"])>0: #Critère pour vérifier qu'il s'agit bien d'un train - à remplacer éventuellement
                j=j+1
                tab.loc[j]=0
                for i in range(len(cols)):
                    c=cols[i]
                    cha=champs[i]
                    try:
                        tab.loc[j,c]=res["results"][n]["priceProposals"][cha]["amount"]
                    except:
                        pass
                tab.loc[j,"numéro train"]=res["results"][n]["segments"][0]["trainNumber"]
                print(" Réussi")
    except:
        print(" Raté")
        pass
    nrows=tableau_donnees.shape[0]
    t=tableau_donnees.loc[range(nrows-vrai_nb_trains,nrows),["Date rech","numéro train"]].copy()
    t=t.merge(tab,how="left",on="numéro train")
    print(t)
    tableau_donnees.loc[:,cols+["numéro train"]]=t.loc[:,cols+["numéro train"]]


headers = {
    'Host': 'www.oui.sncf',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json;charset=utf-8',
    'X-VSD-SMART-GUY-GUARD': 'SdulvOlooN5;44534:T4QQRZD\\',
    'X-VSD-LOCALE':'fr_FR',
    'Referer': 'https://www.oui.sncf/proposition?clientId=8cf49d04-2ced-400e-838f-18056a134b51&language=fr&country=FR',
    'Content-Length': '1129',
    'Connection': 'keep-alive'
}

url='https://www.voyages-sncf.com/proposition/rest/search-travels/outward'

##############################
####Paramètres en entrée
#dataEntree
villes_depart=['Paris']
villes_arrivee=['Lille','Lyon','Toulouse','Bordeaux','Marseille','Strasbourg','Brest','Rouen']
list_ant=[(0,10),(1,0),(2,0),(3,0)] #(format : (mois,jours))
horaires=['08:00:00','11:00:00','14:00:00','17:00:00','21:00:00']
#Calcul des jours recherchés
jour_req = datetime.datetime.now()
dates=[]
for anteriorite in list_ant:
  jour_rech=jour_req+relativedelta(days=anteriorite[1],months=anteriorite[0])
  jour_rech_format = "{:d}-{:02d}-{:02d}".format(jour_rech.year,jour_rech.month,jour_rech.day)
  dates.append(jour_rech_format)



#Pour faire un petit test, mini-échantillon
villes_depart=['Paris']
villes_arrivee=['Biarritz']
dates=['2018-01-16']
horaires=['08:00:00']
#
#
#nb_obs=len(villes_depart)*len(villes_arrivee)*len(dates)*len(horaires)
##On crée le tableau avec juste les noms des colonnes
#tableau_result=pd.DataFrame(index=[],columns=["Départ rech","Arrivée rech","Date rech","Heure rech","Gare dép","Gare arriv","Date dép","Heure dép","Date arriv","Heure arriv","Type","Prix noflex_classe2","Prix semiflex_classe2","Prix flex_classe2","Prop classe1","numéro train","antériorité","Prix noflex_classe1","Prix semiflex_classe1","Prix flex_classe1","Prix noflex_classe2_jeune","Prix semiflex_classe2_jeune","Prix flex_classe2_jeune","Prop classe1_jeune","Prix noflex_classe2_sénior","Prix semiflex_classe2_sénior","Prix flex_classe2_sénior","Prop classe1_sénior"])
#

nb_obs=len(villes_depart)*len(villes_arrivee)*len(dates)*len(horaires)
tableau_result=pd.DataFrame(np.zeros(shape=(nb_obs,28)))
#Noms des colonnes
tableau_result.columns=["Départ rech","Arrivée rech","Date rech","Heure rech","Gare dép","Gare arriv","Date dép","Heure dép","Date arriv","Heure arriv","Type","Prix noflex_classe2","Prix semiflex_classe2","Prix flex_classe2","Prop classe1","numéro train","antériorité","Prix noflex_classe1","Prix semiflex_classe1","Prix flex_classe1","Prix noflex_classe2_jeune","Prix semiflex_classe2_jeune","Prix flex_classe2_jeune","Prop classe1_jeune","Prix noflex_classe2_sénior","Prix semiflex_classe2_sénior","Prix flex_classe2_sénior","Prop classe1_sénior"]


j=-1
for ville_depart in villes_depart:
    for ville_arrivee in villes_arrivee:
        for date in dates:
            for horaire in horaires:

                #On concatène pour avoir notre json de demande
                demande1='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":26,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                #On effectue la requête
                r = requests.post(url, data=demande1,headers=headers)

                #La requête a-t-elle fonctionné ? On veut 200
                print("Billet " + ville_depart + "-" + ville_arrivee + "   Statut : "+str(r))

                #Voici notre résultat ; il faut nettoyer la chaîne de caractères maintenant
                resultat=nettoyage(r.text)

                #Conversion en json
                try:
                    resultat3=json.loads(resultat)
                    nb_trains=len(resultat3["results"])
                    vrai_nb_trains=0
                    for n in range(nb_trains):

                        if len(resultat3["results"][n]["priceProposals"])>0: #Critère pour vérifier qu'il s'agit bien d'un train - à remplacer éventuellement
                            j=j+1
                            vrai_nb_trains=vrai_nb_trains+1
                            if j>-1:
                                tableau_result.loc[j]=0
                            #On inscrit dans le tableau les paramètres d'entrée
                            tableau_result.iloc[j,0:4]=[ville_depart,ville_arrivee,date,horaire]

                            ##On inscrit dans le talbeau les résultats
                            #D'abord les villes de départ, arrivée, la date et les horaires effectifs :
                            tableau_result.loc[j,"Gare dép"]=resultat3["results"][n]["origin"]
                            tableau_result.loc[j,"Gare arriv"]=resultat3["results"][n]["destination"]
                            tableau_result.loc[j,"Date dép"]=resultat3["results"][n]["departureDate"].split("T")[0]
                            tableau_result.loc[j,"Heure dép"]=resultat3["results"][n]["departureDate"].split("T")[1]
                            tableau_result.loc[j,"Date arriv"]=resultat3["results"][n]["arrivalDate"].split("T")[1]
                            tableau_result.loc[j,"Heure arriv"]=resultat3["results"][n]["departureDate"].split("T")[0]

                            #Le type de transport :
                            tableau_result.loc[j,"Type"]=resultat3["results"][n]["segments"][0]["transporter"]
                            nb_correspondances=len(resultat3["results"][n]["segments"])
                            i=0
                            while i+1<nb_correspondances:
                                i=i+1
                                tableau_result.loc[j,"Type"]=tableau_result.loc[j,"Type"]+" puis "+resultat3["results"][n]["segments"][i]["transporter"]

                            #Puis les prix !
                            try:
                                tableau_result.loc[j,"Prix noflex_classe2"]=resultat3["results"][n]["priceProposals"]["NOFLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.loc[j,"Prix semiflex_classe2"]=resultat3["results"][n]["priceProposals"]["SEMIFLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.loc[j,"Prix flex_classe2"]=resultat3["results"][n]["priceProposals"]["FLEX"]["amount"]
                            except:
                                pass
                            try:
                                tableau_result.loc[j,"Prop classe1"]=resultat3["results"][n]["priceProposals"]["UPSELL"]["amount"]
                            except:
                                pass

                            #Enfin, le numéro du train et la classe d'antériorité
                            tableau_result.loc[j,"numéro train"]=resultat3["results"][n]["segments"][0]["trainNumber"]
                            tableau_result.loc[j,"antériorité"]=str(calcul_anteriorite(date,datetime.datetime.now()))+" jours"
                            print(" Réussi")

                except:
                    print(" Raté")
                    pass
#
                #Maintenant la deuxième demande, 1ère classe :
                demande_1e='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"FIRST","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":36,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_1e = requests.post(url, data=demande_1e,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " 1ère classe" + "   Statut : "+str(r_1e))
                resultat_1e=nettoyage(r_1e.text)
                #On remplit
                cols_1e=["Prix noflex_classe1","Prix semiflex_classe1","Prix flex_classe1"]
                remplir(tableau_result,resultat_1e,cols_1e,["NOFLEX","SEMIFLEX","FLEX"],nb_trains)


                #Maintenant la troisième demande, carte jeune :
                demande_jeune='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"YOUNG","age":22,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"YOUNGS","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_jeune = requests.post(url, data=demande_jeune,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " Carte jeune" + "   Statut : "+str(r_jeune))
                resultat_jeune=nettoyage(r_jeune.text)
                #On remplit
                cols_jeune=["Prix noflex_classe2_jeune","Prix semiflex_classe2_jeune","Prix flex_classe2_jeune","Prop classe1_jeune"]
                remplir(tableau_result,resultat_jeune,cols_jeune,["NOFLEX","SEMIFLEX","FLEX","UPSELL"],nb_trains)


                #Maintenant la quatrième demande, carte sénior :
                demande_senior='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"SENIOR","age":66,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"SENIOR","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_senior = requests.post(url, data=demande_senior,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " Carte sénior" + "   Statut : "+str(r_senior))
                resultat_senior=nettoyage(r_senior.text)
                #On remplit
                cols_senior=["Prix noflex_classe2_sénior","Prix semiflex_classe2_sénior","Prix flex_classe2_sénior","Prop classe1_sénior"]
                remplir(tableau_result,resultat_senior,cols_senior,["NOFLEX","SEMIFLEX","FLEX","UPSELL"],nb_trains)



#%%
#On exporte en csv
import datetime
date = datetime.datetime.now()
tableau_result.to_csv("SNCF_"+str(date.year)+str(date.month)+str(date.day)+"_"+"{:d}h{:02d}".format(date.hour, date.minute)+".csv")


#%%Pour copier quelque-chose dans le presse-papier

import pyperclip
pyperclip.copy(resultat_senior)



#%%
a=pd.DataFrame(np.arange(20).reshape((4,5)))
a

def f_test(a):
    b=a.copy()
    b[:].loc[range(2,3),:]=0
    return b

f_test(a)
a

i=7

def f_t(i):
    j=i
    j=j+1
    return j

f_t(i)
i








C = np.arange(12)
for c in C:
    c += 1
print(C)