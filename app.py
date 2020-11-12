#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 01:07:31 2020

@author: albanilm
"""

import mysql.connector
import time
from trello import TrelloClient
import json
import sys
import os

#trello credentials
TKEY = "0583727d23603125a162e7fb33e02d5e"
TTOKEN = "079e68a4f914beeb676dd07d1fa4c1c77d7687ec395d0ea5eb4a6f47cc24ca18"
TBOARD_NAME = "ARPIC"
TBOARD_BACKLOG_NAME = "BACKLOG"
TBOARD_BACKLOG_ID = ""
TLABELS_BOARD = ["contact_form", "facebook", "twitter", "survey"]

#RDS credentials
RDSHOST = "db-arpic.cjdm15sdlirv.us-east-1.rds.amazonaws.com"
RDSUSER = "adminarpic" 
RDSPASS = "adminarpic$2020"
RDSDB = "arpic"

LIMITCARDS = 1
CRON_TIME = 20



def arpicAddcard(obj_labels,obj_list,data):
    label_to_add = next(x for x in obj_labels if x.name == str(data[2]))
    obj_list.add_card(str(data[0]),str(data[1]),[label_to_add]) 
   # obj_list.add_card(data[0],data[1],[label_to_add]) 

def arpicGetLastRdsTrelloCard(rds_cursor):
    query = ("SELECT value FROM arpic.arpic_parameters where parameter = 'rds_trello_card' limit 1")
    rds_cursor.execute(query)
    rst = rds_cursor.fetchone()
    return int(rst[0])

def arpicSetLastRdsTrelloCard(mydb,last_id_card):
    rds_cursor = mydb.cursor()
    query = ("UPDATE arpic.arpic_parameters SET value = '"+str(last_id_card)+"' WHERE parameter = 'rds_trello_card' limit 1")
    rds_cursor.execute(query)
    mydb.commit()
    return int(rds_cursor.rowcount)

def arpicGetRdsMessages(rds_cursor,last_id_card):
    query = ("SELECT * FROM arpic.arpic_messages where id > " + str(last_id_card) + " limit "+ str(LIMITCARDS))
    rds_cursor.execute(query)
    rst = rds_cursor.fetchall()
    return rst

def arpicFriendlyTitle(obj_title,label):
    ct = json.loads(obj_title)
    if label == 'contact_form':
        return ct['email']
    elif label == 'twitter': 
        return "@"+ct['account']
    elif label == 'survey': 
        return ct['email']      
    else:
        return obj_title

def arpicFriendlyBody(obj_title,obj_body,label):
    ct = json.loads(obj_title)
    if label == 'contact_form':
        ds_description = "%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % \
            ("CONTACTO",
            "===",
            "***Nombre:*** "+ct['name'],
            "***Email:*** "+ct['email'],
            "***Telefono:*** "+ct['phone'],
            "MENSAJE",
            "===",
            obj_body)  
    elif label == 'twitter':   
        ds_description = "%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % \
            ("CONTACTO",
            "===",
            "***Nombre:*** "+ct['name'],
            "***Cuenta:*** @"+ct['account'],
            "***Id:*** "+str(ct['id']),
            "***Seguidores:*** "+str(ct['followers_count']),
            "***Amigos:*** "+str(ct['friends_count']),
            "MENSAJE",
            "===",
            obj_body)
    if label == 'survey':
        ds_description = "%s\n%s\n%s\n%s\n%s\n%s\n" % \
            ("CONTACTO",
            "===",
            "***Email:*** "+ct['email'],
            "AUDIO",
            "===",
            obj_body)              
    else:
        ds_description = "%s" % \
            ("SIN NADA")
    
    return ds_description

    
def main():   
    #RDS flow
    mydb = mysql.connector.connect(
      host=RDSHOST,
      user=RDSUSER,
      password=RDSPASS,
      database=RDSDB
    )
    cursor = mydb.cursor()
    lastCard = arpicGetLastRdsTrelloCard(cursor)
    rdsMesagges = arpicGetRdsMessages(cursor,lastCard)

    #...................................................  
    #trello flow
    client = TrelloClient(
        api_key=TKEY,
        api_secret=TTOKEN
    )

    for board in client.list_boards():
        if board.name == TBOARD_NAME:
            TBOARD_OBJ = board
            

    for mlist in TBOARD_OBJ.list_lists():
        if mlist.name == TBOARD_BACKLOG_NAME:
            TLIST_OBJ = mlist
    
    TLABELS = TBOARD_OBJ.get_labels()
    #...................................................
    
    if rdsMesagges :    
        #Create card
        rdsCardId = 0
        for x in rdsMesagges:
            rdsCardId = int(x[0])
            rdsTitle = arpicFriendlyTitle(x[3],x[2])
            rdsDescription = arpicFriendlyBody(x[3],x[4],x[2])
            data = [rdsTitle,rdsDescription,x[2]]
            arpicAddcard(TLABELS,TLIST_OBJ,data)
            print("- Add trello card:" + str(rdsCardId) )
            
        #arpicSetLastRdsTrelloCard(mydb,rdsCardId)
    else:
        print("- Not new messages.")
   
    

if __name__ == '__main__':
    main()
    #while True:
        #lc_start = os.environ['ARP_START']
     #   lc_start = 1
     #   if lc_start == 1:
     #       main()
            #time.sleep(CRON_TIME)
    #        print("Scanning RDS messages V2...")
    
