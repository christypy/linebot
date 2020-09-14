import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
from linebot.exceptions import LineBotApiError,InvalidSignatureError
from linebot.models import TemplateSendMessage, CarouselTemplate, CarouselColumn, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
import requests
from bs4 import BeautifulSoup
from time import sleep
import time
import json
import urllib
import sys
import json
import pyshorteners

logger = logging.getLogger("django")

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)

s = pyshorteners.Shortener()

def serach(name):
    s_url='https://www.bookwalker.com.tw/search?w='+urllib.parse.quote(name.encode('utf8'))+'&m=0'
    r=requests.get(s_url)
    soup=BeautifulSoup(r.text,'html.parser')
    book_detail=[]
    for j in soup.select('.bwbookitem'):
        
        book_split=j.text.replace('\n','').split()
        book_detail.append(','.join(book_split))
        
        
    book_link=[s.tinyurl.short(j['href']) for j in  soup.select('.bwbookitem >a')]
   
    return dict(zip(book_detail, book_link))
def serach_watsons(name):
    s_url='https://www.watsons.com.tw/search2?text='+name
    r=requests.get(s_url)
    soup=BeautifulSoup(r.text,'html.parser')
    watsons_detail=[]
    for j in soup.select('.productNameInfo'):
        
        watsons_split=j.text.replace('\n','').replace('\xa0','').replace('\t','').split('$')[:2]


        watsons_detail.append(','.join(watsons_split))
    watsons_link=[s.tinyurl.short(j['href']) for j in  soup.select('.productNameInfo >a')]
    return dict(zip(watsons_detail, watsons_link))

def sleeptime(hour,min,sec):
    return hour*3600 + min*60 + sec
second = sleeptime(0,0,4)   

track_dict={}
track_list=[]
def track(name,track_price):
    list_name=[i['name']for i in track_list]
    if name not in list_name:
        track_dict={'name':name,'price':track_price}
        track_list.append(track_dict)
    
    return track_list
    
    
def while_do(track_list) :
    # while 1==1:
    print('track_list',track_list)
    for book in track_list:
        now_price=int([i.split(',')[-1] for i in serach(book['name'])][0].replace('元',''))
        if now_price <book['price']:
            return serach(book['name'])
        else:
            return str(book['name'])+'價格尚未低於'+str(book['price'])
        # time.sleep(second)



@csrf_exempt
@require_POST
def index(request: HttpRequest):
    signature = request.headers["X-Line-Signature"]
    body = request.body.decode()

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        messages = (
            "Invalid signature. Please check your channel access token/channel secret."
        )
        logger.error(messages)
        return HttpResponseBadRequest(messages)
    return HttpResponse("OK")


@handler.add(event=MessageEvent, message=TextMessage)
def handl_message(event: MessageEvent):
    print('event.message.text',event.message.text)

    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        if '追蹤' in event.message.text:
            
            split_txt=event.message.text.split(' ')
            print('split_txt',split_txt)
            print(while_do(track(split_txt[1],split_txt[2])))
            # line_bot_api.reply_message(
            #     reply_token=event.reply_token,
            #     messages=TextSendMessage(text=)),
        
            
        if '小區' in event.message.text:
            split_txt=event.message.text.split(' ')
            # print('split_txt',split_txt)
            # print(serach_watsons(split_txt[1]))
            watsons_dict=serach_watsons(split_txt[1])
            dictlist=[','.join([k,v])for k,v in watsons_dict.items()]
            if len (dictlist)==0:
                line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text='尚未有此產品')),
            else:
                line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text=' '.join(dictlist) )),
             

        else:
            bppl_dict=serach(event.message.text)
            
            dictlist=[','.join([k,v])for k,v in bppl_dict.items()]
            if len (dictlist)==0:
                line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text='尚未有這本書')),
            else:
                line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text=' '.join(dictlist) )),
             

            
