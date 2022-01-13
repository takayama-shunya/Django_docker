from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse
from ..models import Service_Stock
from ..forms import ServiceStockForm
from words.forms import ServiceItemForm
from words.models import Service_Item
from utils.views.encoder import Encode
import logging

logger = logging.getLogger(__name__)

class SelectUpdateServiceStock(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'peace_keeping/service_stock/update_serv/select_update_serv.html')

    def post(self, request, *args, **kwargs):
        area_name = request.POST['area_name']
        serv_name = request.POST['serv_name']
        serv_stocks = Service_Stock.objects.filter(serv_name=serv_name, area__name=area_name).all()
        target_serv_stock = None
        latest_ver = -1
        for serv_stock in serv_stocks:
            if latest_ver<serv_stock.ver:
                latest_ver = serv_stock.ver
                target_serv_stock = serv_stock
        logger.debug('[latest_ver] {}'.format(latest_ver))
        target_serv_id = target_serv_stock.serv_id
        logger.debug('[target_serv_id] {}'.format(target_serv_id))
        if len(serv_stocks)==0:
            raise Exception('Given the pair of area_name and serv_name does not exist.')
        core_items = list(str(target_serv_stock.core_items_serial).split("|"))
        opt_items = list(str(target_serv_stock.opt_items_serial).split("|"))
        context = {'area_name': area_name, 'serv_name': serv_name, 'ex_serv_id': target_serv_id, 'core_items': core_items, 'opt_items': opt_items}
        return render(request, 'peace_keeping/service_stock/update_serv/input_update_serv.html', context)

class ConfirmUpdateServiceStock(View):
    def post(self, request, *args, **kwargs):
        area_name = request.POST['area_name']
        serv_name = request.POST['serv_name']
        ex_serv_id = request.POST['ex_serv_id']
        new_items=[]
        idx=0
        key="new_item"+str(idx)
        while key in request.POST.keys():
            new_items.append(request.POST[key])
            idx+=1
            key="new_item"+str(idx)
        parts = list(ex_serv_id.split("-"))
        new_version = str( int(parts[-1])+1 )
        logger.info(f'[area_name] {area_name}/ 内閣中央省庁の場合はコア項目、それ以外はオプション項目として保存されます')
        if area_name=="内閣中央省庁":
            new_core_serv_id = Encode.core_serv_id(new_items)
            new_serv_id = parts[0]+new_core_serv_id+"-"
            if parts[1][0]=="o": # opt exists
                new_serv_id += parts[1]+"-"+parts[2]+"-"+new_version
            else:
                new_serv_id += parts[1]+"-"+new_version
        else:
            logger.warn("opt_idはない場合生成されるようにする")
            new_opt_serv_id = Encode.opt_serv_id(new_items)
            new_serv_id = parts[0]+"-"
            if parts[1][0]=="o": # opt exists
                new_serv_id += parts[1]+new_opt_serv_id+"-"+parts[2]+"-"+new_version
            else:
                new_serv_id += new_opt_serv_id+"-"+parts[1]+"-"+new_version
        logger.debug('[pre_serv_id] {}'.format(ex_serv_id))
        logger.debug('[new_serv_id] {}'.format(new_serv_id))
        context = {'area_name': area_name, 'serv_name': serv_name, 'ex_serv_id': ex_serv_id, 'new_serv_id': new_serv_id, 'new_items': new_items}
        return render(request, 'peace_keeping/service_stock/update_serv/confirm_update_serv.html', context)


class ResultUpdateServiceStock(View):
    def post(self, request, *args, **kwargs):
        ex_serv_id = request.POST['ex_serv_id']
        new_serv_id = request.POST['new_serv_id']
        new_version = int(new_serv_id.split("-")[-1])
        serv_name = request.POST['serv_name']
        area_name = request.POST['area_name']
        core_serv_ids_str = list( new_serv_id.split('-')[0].split("c")[1:] )
        core_serv_ids = ["c"+core_serv_ids_str[i] for i in range(len(core_serv_ids_str))]
        opt_serv_ids_str = list( new_serv_id.split('-')[1].split("o")[1:] )
        opt_serv_ids = ["o"+opt_serv_ids_str[i] for i in range(len(opt_serv_ids_str))]
        phrases = []
        core_items = []
        for core_item_id in core_serv_ids:
            serv_item = Service_Item.objects.filter(core_item_id=core_item_id, is_core_std=True)
            if serv_item.exists():
                phrases.append(serv_item.get().phrase)
                core_items.append(serv_item.get().phrase)
        opt_items = []
        for opt_item_id in opt_serv_ids:
            serv_item = Service_Item.objects.filter(opt_item_id=opt_item_id, is_opt_std=True)
            if serv_item.exists():
                phrases.append(serv_item.get().phrase)
                opt_items.append(serv_item.get().phrase)
        res_id = Service_Stock.update_save_serv_stock(serv_name, area_name, core_items=core_items, opt_items=opt_items, ver=new_version, ex_serv_id=ex_serv_id)
        logger.debug('[result_id] {}'.format(res_id))
        context={'new_serv_id': res_id, 'ex_serv_id': ex_serv_id}
        return render(request, 'peace_keeping/service_stock/update_serv/result_update_serv.html', context)
