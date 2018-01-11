# -*- coding: utf-8 -*-

# Define here the models for your DB
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html


def get_value():
    return _global_db
class GlobalVar:
    db_handle = None
    mq_client = None
def set_db_handle(db):
    GlobalVar.db_handle = db
def get_db_handle():
    return GlobalVar.db_handle
def set_mq_client(mq_cli):
    GlobalVar.mq_client = mq_cli
def get_mq_client():
    return GlobalVar.mq_client
