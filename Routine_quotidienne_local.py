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
import os
import time
import schedule

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

#Import de la fonction remplir
from Routine_quotidienne import remplir

def collecte():
    #path
    os.chdir('D:/NHNBYB/Mes Documents/Webscraping/Scraping SNCF/')
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
    ####Parametres en entree
    #Tables des origines et destinations
    trajets=pd.read_csv("Input/origines_destinations.csv",sep=";",encoding="latin-1",)
    dim_trajets=trajets.shape[0]
    #Anteriorites
    list_ant=[(0,2),(0,10),(0,30),(0,60),(0,90)] #(format : (mois,jours))
    #Horaires recherches
    horaires=['08:00:00','11:00:00','14:00:00','17:00:00','21:00:00']
    #Calcul des jours recherches
    jour_req = datetime.datetime.now()
    dates=[]
    for anteriorite in list_ant:
      jour_rech=jour_req+relativedelta(days=anteriorite[1],months=anteriorite[0])
      jour_rech_format = "{:d}-{:02d}-{:02d}".format(jour_rech.year,jour_rech.month,jour_rech.day)
      dates.append(jour_rech_format)

    #Pour faire un petit test, mini-echantillon
#    trajets=pd.DataFrame([['Paris','Biarritz']])
#    dim_trajets=trajets.shape[0]
#    trajets.columns=["Origine","Destination"]
    #dates=['2018-01-16']
    #horaires=['08:00:00','12:00:00']

    variables_utiles=["Depart rech","Arrivee rech","Date rech","Heure rech","Gare dep","Gare arriv","Date dep","Heure dep","Date arriv","Heure arriv","Type","Prix noflex_classe2","Prix semiflex_classe2","Prix flex_classe2","Prop classe1","numero train","anteriorite","Prix noflex_classe1","Prix semiflex_classe1","Prix flex_classe1","Prix noflex_classe2_jeune","Prix semiflex_classe2_jeune","Prix flex_classe2_jeune","Prop classe1_jeune","Prix noflex_classe2_senior","Prix semiflex_classe2_senior","Prix flex_classe2_senior","Prop classe1_senior"]

    #Creer notre dossier d'output
    date_today = datetime.datetime.now()
    output_directory="Output/SNCF_"+"{:d}-{:02d}-{:02d}-{:02d}h{:02d}".format(date_today.year, date_today.month, date_today.day, date_today.hour, date_today.minute)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    fichiers_crees=[]
    for traj in range(dim_trajets):
        ville_depart=trajets.loc[traj,"Origine"]
        ville_arrivee=trajets.loc[traj,"Destination"]
        for date in dates:
            j=-1
            #On cree un nouveau tableau pour chaque trajet*date, qu'on exportera ensuite, et à la fin on concatenera le tout
            tableau_result=pd.DataFrame(np.zeros(shape=(1,len(variables_utiles))))
            #Noms des colonnes
            tableau_result.columns=variables_utiles
            for horaire in horaires:

                #On concatene pour avoir notre json de demande
                demande1='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":26,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                #On effectue la requête
                r = requests.post(url, data=demande1,headers=headers)

                #La requête a-t-elle fonctionne ? On veut 200
                print("Billet " + ville_depart + "-" + ville_arrivee + "   Statut : "+str(r))

                #Voici notre resultat ; il faut nettoyer la chaîne de caracteres maintenant
                resultat=nettoyage(r.text)

                #Conversion en json
                try:
                    resultat3=json.loads(resultat)
                    nb_trains=len(resultat3["results"])
                    vrai_nb_trains=0
                    for n in range(nb_trains):

                        if len(resultat3["results"][n]["priceProposals"])>0: #Critere pour verifier qu'il s'agit bien d'un train - à remplacer eventuellement
                            if j==-1:
                                j=0
                            elif resultat3["results"][n]["segments"][0]["trainNumber"]!=tableau_result.loc[j,"numero train"]:
                                j=j+1
                            elif resultat3["results"][n]["departureDate"].split("T")[1]!=tableau_result.loc[j,"Heure dep"]:
                                j=j+1
                            elif resultat3["results"][n]["arrivalDate"].split("T")[1]!=tableau_result.loc[j,"Heure arriv"]:
                                j=j+1
                            else:
                                continue
                            vrai_nb_trains=vrai_nb_trains+1
                            tableau_result.loc[j]=0
                            #On inscrit dans le tableau les parametres d'entree
                            tableau_result.iloc[j,0:4]=[ville_depart,ville_arrivee,date,horaire]
                            ##On inscrit dans le talbeau les resultats
                            #D'abord les villes de depart, arrivee, la date et les horaires effectifs :
                            tableau_result.loc[j,"Gare dep"]=resultat3["results"][n]["origin"]
                            tableau_result.loc[j,"Gare arriv"]=resultat3["results"][n]["destination"]
                            tableau_result.loc[j,"Date dep"]=resultat3["results"][n]["departureDate"].split("T")[0]
                            tableau_result.loc[j,"Heure dep"]=resultat3["results"][n]["departureDate"].split("T")[1]
                            tableau_result.loc[j,"Date arriv"]=resultat3["results"][n]["arrivalDate"].split("T")[0]
                            tableau_result.loc[j,"Heure arriv"]=resultat3["results"][n]["arrivalDate"].split("T")[1]
                            #Le type de transport :
                            tableau_result.loc[j,"Type"]=resultat3["results"][n]["segments"][0]["transporter"]
                            nb_correspondances=len(resultat3["results"][n]["segments"])
                            i=0
                            while i+1<nb_correspondances:
                                i=i+1
                                tableau_result.loc[j,"Type"]=tableau_result.loc[j,"Type"]+" puis "+resultat3["results"][n]["segments"][i]["transporter"]
                            #Puis les prix ! Differents prix recherches
                            cols_gen=["Prix noflex_classe2","Prix semiflex_classe2","Prix flex_classe2","Prop classe1"]
                            tarifs=["NOFLEX","SEMIFLEX","FLEX","UPSELL"]
                            for a in range(4):
                                try:
                                    tableau_result.loc[j,cols_gen[a]]=resultat3["results"][n]["priceProposals"][tarifs[a]]["amount"]
                                except:
                                    pass
                            #Enfin, le numero du train et la classe d'anteriorite
                            tableau_result.loc[j,"numero train"]=resultat3["results"][n]["segments"][0]["trainNumber"]
                            tableau_result.loc[j,"anteriorite"]=str(calcul_anteriorite(date,datetime.datetime.now()))+" jours"
    #                        print(" Reussi")
                except:
                    print(" Rate")
                    pass
    #
                #Maintenant la deuxieme demande, 1ere classe :
                demande_1e='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"FIRST","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"ADULT","age":36,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"NONE","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_1e = requests.post(url, data=demande_1e,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " 1ere classe" + "   Statut : "+str(r_1e))
                resultat_1e=nettoyage(r_1e.text)
                #On remplit
                cols_1e=["Prix noflex_classe1","Prix semiflex_classe1","Prix flex_classe1"]
                remplir(tableau_result,resultat_1e,cols_1e,["NOFLEX","SEMIFLEX","FLEX"],vrai_nb_trains)

                #Maintenant la troisieme demande, carte jeune :
                demande_jeune='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"YOUNG","age":22,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"YOUNGS","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_jeune = requests.post(url, data=demande_jeune,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " Carte jeune" + "   Statut : "+str(r_jeune))
                resultat_jeune=nettoyage(r_jeune.text)
                #On remplit
                cols_jeune=["Prix noflex_classe2_jeune","Prix semiflex_classe2_jeune","Prix flex_classe2_jeune","Prop classe1_jeune"]
                remplir(tableau_result,resultat_jeune,cols_jeune,["NOFLEX","SEMIFLEX","FLEX","UPSELL"],vrai_nb_trains)

                #Maintenant la quatrieme demande, carte senior :
                demande_senior='{"origin":"'+ville_depart+'","originLocation":{"id":null,"label":null,"longitude":null,"latitude":null,"type":null,"country":null,"stationCode":null,"stationLabel":null},"destination":"'+ville_arrivee+'","destinationCode":null,"destinationLocation":null,"directTravel":false,"asymmetrical":false,"professional":false,"customerAccount":false,"oneWayTravel":true,"departureDate":"'+date+'T'+horaire+'","returnDate":null,"travelClass":"SECOND","country":"FR","language":"fr","busBestPriceOperator":null,"passengers":[{"travelerId":null,"profile":"SENIOR","age":66,"birthDate":null,"fidelityCardType":"NONE","fidelityCardNumber":null,"commercialCardNumber":null,"commercialCardType":"SENIOR","promoCode":"","lastName":null,"firstName":null,"phoneNumer":null,"hanInformation":null}],"animals":[],"bike":"NONE","withRecliningSeat":false,"physicalSpace":null,"fares":[],"withBestPrices":false,"highlightedTravel":null,"nextOrPrevious":false,"source":"FORM_SUBMIT","targetPrice":null,"han":false,"outwardScheduleType":"BY_DEPARTURE_DATE","inwardScheduleType":"BY_DEPARTURE_DATE","$initial":true,"$queryId":"WDDI9"}'
                r_senior = requests.post(url, data=demande_senior,headers=headers)
                print("Billet " + ville_depart + "-" + ville_arrivee + " Carte senior" + "   Statut : "+str(r_senior))
                resultat_senior=nettoyage(r_senior.text)
                #On remplit
                cols_senior=["Prix noflex_classe2_senior","Prix semiflex_classe2_senior","Prix flex_classe2_senior","Prop classe1_senior"]
                remplir(tableau_result,resultat_senior,cols_senior,["NOFLEX","SEMIFLEX","FLEX","UPSELL"],vrai_nb_trains)


            #On exporte en csv
            nomFichier = "SNCF_"+str(date)+"_"+ville_depart+" - "+ville_arrivee+"_"+str(calcul_anteriorite(date,datetime.datetime.now()))+" jours.csv"
            tableau_result.to_csv(output_directory+"/"+nomFichier)
            fichiers_crees.append(nomFichier)


    #Maintenant on importe tous les csv et on concatene (-> un fichier par date de trajet)
    os.chdir('D:/NHNBYB/Mes Documents/Webscraping/Scraping SNCF/'+output_directory)
    for anteriorite in list_ant:
        #On initialise une table
        table_antfixee=pd.DataFrame()
        for v in variables_utiles:
            table_antfixee[v]=0
        for nom in fichiers_crees:
            if nom.split("_")[3]==str(anteriorite[1])+" jours.csv":
                no=nom.split("_")
                lecture_fichier=pd.read_csv(nom,sep=";",encoding="latin-1",)
                table_antfixee=pd.concat([table_antfixee,lecture_fichier])
        table_antfixee.to_csv("Collecte_"+no[1]+"_"+no[3]+".csv")




##############################################
##On veut lancer notre programme tous les jours à la même heure
#start_time = time.time()
#
#schedule.every().day.at("01:15").do(collecte)
#print("On a lance la tâche")
#
#while True:
#    schedule.run_pending()
#    time.sleep(60) # wait one minute
#
#print("--- %s seconds ---" % (time.time() - start_time))
##############################################

collecte()
