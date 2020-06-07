import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

from accounts.models import *
from .models import Store, OrderList
from ceos.forms import StoreForm


def is_manager(user, store):
    if store.manager == user:
        return True
    else:
        return False


@login_required
def index(request):
    if request.user.auth_code == 2:
        stores = Store.objects.filter(manager=request.user)
        context = {
            'stores': stores,
        }
        return render(request, 'ceos/index.html', context)
    else:
        return redirect('main:index')


@login_required
def create_store(request):
    if request.user.auth_code == 2:
        store_form = StoreForm(request.POST, request.FILES)
        if store_form.is_valid():
            store = store_form.save(commit=False)
            store.manager = request.user
            store.save()
            return redirect('ceos:index')
        else:
            store_form = StoreForm()
        context = {
            'store_form': store_form,
        }
        return render(request, 'ceos/form_store.html', context)
    else:
        return redirect('main:index')


@login_required
def update_store(request, store_pk):
    if request.user.auth_code == 2:
        store = get_object_or_404(Store, pk=store_pk)
        if request.user == store.manager:
            store_form = StoreForm(request.POST, instance=store)
            if store_form.is_valid():
                store = store_form.save(commit=False)
                store.manager = request.user
                store.save()
                return redirect('ceos:index')
            else:
                store_form = StoreForm(instance=store)
            context = {
                'store_form': store_form,
            }
            return render(request, 'ceos/form_store.html', context)
        else:
            return redirect('ceos:index')
    else:
        return redirect('main:index')


@login_required
def detail_store(request, store_pk):
    if request.user.auth_code == 2:
        store = get_object_or_404(Store, pk=store_pk)
        if request.user == store.manager:
            menu_list = store.storemenu_set.all()
            context = {
                'store': store,
                'menu_list': menu_list,
            }
            return render(request, 'ceos/detail_store.html', context)
        else:
            return redirect('ceos:index')
    else:
        return redirect('main:index') 


def orders(request, store_pk):
    store = get_object_or_404(Store, pk=store_pk)
    user = request.user
    if is_manager(user, store):
        orders = store.orderlist_set.all().order_by('-pk')
        paginator = Paginator(orders, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = { 'orders': page_obj }
        return render(request, 'ceos/orders.html', context)
    else:
        return redirect('main:index')


def set_condition(request):
    data = json.loads(request.body.decode('utf-8'))
    order = get_object_or_404(OrderList, pk=data['params']['order_pk'])
    if is_manager(request.user, order.store):
        order_condition = data['params']['order_condition']
        order.order_condition = order_condition
        order.save()
        context = {
            'message': 'OK',
            'orderConditon': order_condition,
        }
        return JsonResponse(context)
    else:
        context = {
            'message': 'ERROR',
        }
        return JsonResponse(context)


def order_delete(request):
    data = json.loads(request.body.decode('utf-8'))
    order = get_object_or_404(OrderList, pk=data['params']['order_pk'])
    if is_manager(request.user, order.store):
        # 환불 절차를 수행하는 것이 맞다고 생각함.
        order.delete()
        context = {
            'message': 'OK',
        }
        return JsonResponse(context)
    else:
        context = {
            'message': 'ERROR',
        }
        return JsonResponse(context)