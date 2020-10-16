#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 01:07:31 2020

@author: albanilm
"""

import mysql.connector
import time
from trello import TrelloClient

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

LIMITCARDS = 3


def arpicAddcard(obj_labels,obj_list,data):
    label_to_add = next(x for x in obj_labels if x.name == str(data[2]))
    obj_list.add_card(data[0],data[1],[label_to_add]) 

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
    
    
    #Create card
    rdsCardId = 0
    for x in rdsMesagges:
        rdsCardId = int(x[0])
        data = [x[3].decode(),x[4].decode(),x[2].decode()]
        arpicAddcard(TLABELS,TLIST_OBJ,data)
        print(int(x[0]))
        
    updlastCard = arpicSetLastRdsTrelloCard(mydb,rdsCardId)
   
   
    

if __name__ == '__main__':
    while True:
        main()
        time.sleep(20)
    
