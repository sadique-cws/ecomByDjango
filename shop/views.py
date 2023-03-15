from django.shortcuts import render,redirect,get_object_or_404
from shop.models import *
from django.contrib.auth.forms import AuthenticationForm
from  django.contrib.auth import authenticate, login as loginFun, logout
from shop.forms import RegisterForm
from django.contrib.auth.decorators import login_required
from .forms import AddressForm

# new imports 
from django.views.decorators.csrf import csrf_exempt
from shop.utils import VerifyPaytmResponse
from . import Checksum
from django.conf import settings
from django.http import HttpResponse

def getCategory():
    return Category.objects.all()

def homepage(r):
    data = {}
    data['category'] = getCategory()
    data['products'] = Product.objects.all()
    return render(r, "home.html",data)

def filterProduct(r,slug):
    data = {}
    data['category'] = getCategory()
    data['products'] = Product.objects.filter(category__slug=slug)
    return render(r, "home.html", data)

def search(r):
    data = {}
    data['category'] = getCategory()
    data['products'] = Product.objects.filter(name__icontains=r.GET.get('search'))
    return render(r, "home.html", data)

def viewProduct(r, slug):
    data = {}
    data['category']  = getCategory()
    data['product'] = Product.objects.get(slug=slug)
    return render(r, "singleView.html", data)

def login(r):
    form = AuthenticationForm(r.POST or None)
    if r.method == "POST":
        username = r.POST.get('username')
        password = r.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            loginFun(r,user)
            return redirect(homepage) 
    data = {}
    data['form'] = form
    return render(r, "login.html", data)

def register(r):
    form = RegisterForm(r.POST or None)
    if r.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(login)
        
    data = {}
    data['form'] = form
    return render(r, "register.html",data)

def signout(r):
    logout(r)
    return redirect(login)
# login required
@login_required()
def addToCart(r,slug):
    product = get_object_or_404(Product, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(user=r.user, ordered=False, item=product)
    order_qs = Order.objects.filter(user=r.user,ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        #order record already exist
        if(order.items.filter(item__slug=slug).exists()):
            order_item.qty += 1
            order_item.save()
        else:
            order.items.add(order_item)
        
        return redirect(myCart)
    else:
        #need to create new order record
        order = Order.objects.create(user=r.user)
        order.items.add(order_item)
        # msg: this item is added to your cart
        return redirect(myCart)
    
@login_required()
def myCart(r):
    data = {}
    data['order'] = Order.objects.get(user=r.user,ordered=False)
    return render(r, "cart.html",data)

@login_required()
def removeFromCart(r,slug):
    product = get_object_or_404(Product, slug=slug)
    order = Order.objects.get(user=r.user,ordered=False)
    order_item = OrderItem.objects.get(user=r.user, ordered=False, item=product)
    if order:
        if(order.items.filter(item__slug=slug).exists()):
            if order_item.qty <= 1:
                order_item.delete()
            else:
                order_item.qty -= 1
                order_item.save()
        return redirect(myCart)

def checkCode(code):
    try:
        coupon = Coupon.objects.get(code=code)
        return True
    except:
        return False
    
def getCoupon(code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon 
    except:
        # invalid coupon
        return redirect(myCart)

def addCoupon(r):
    code = r.POST.get('code')

    if checkCode(code):
        coupon = getCoupon(code)
        order = Order.objects.get(user=r.user, ordered=False)
        order.coupon = coupon
        order.save()
        # successfully coupon applied
    return redirect(myCart)

def removeCoupon(r):
    order = Order.objects.get(user=r.user, ordered=False)
    order.coupon = None
    order.save()
    return redirect(myCart)

def checkout(r):
    form  = AddressForm(r.POST or None)
    addresses = Address.objects.filter(user=r.user)
    if r.method == "POST":
        if form.is_valid():
            f = form.save(commit=False)
            f.user = r.user
            f.save()

            order = Order.objects.get(user=r.user, ordered=False)
            order.address = f
            order.save()

            return HttpResponse("<html><a href='http://localhost:8000/payment'>PayNow</html>")
        
    return render(r, "checkout.html",{"form":form, "addresses":addresses})


def checkoutWithSaveAddress(r):
    if r.method == "POST":
        address_id = r.POST.get('saved_address')
        address = Address.objects.get(pk=address_id)
        order = Order.objects.get(user=r.user, ordered=False)
        order.address = address
        order.save()
        return HttpResponse("<html><a href='http://localhost:8000/payment'>PayNow</html>")


def payment(request):
    order_id = Checksum.__id_generator__()
    bill_amount = "5"
    data_dict = {
        'MID': settings.PAYTM_MERCHANT_ID,
        'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
        'WEBSITE': settings.PAYTM_WEBSITE,
        'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
        'CALLBACK_URL': settings.PAYTM_CALLBACK_URL,
        'MOBILE_NO': '7405505665',
        'EMAIL': 'dhaval.savalia6@gmail.com',
        'CUST_ID': str(request.user.id),
        'ORDER_ID':order_id,
        'TXN_AMOUNT': bill_amount,
    } # This data should ideally come from database
    data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, settings.PAYTM_MERCHANT_KEY)
    context = {
        'payment_url': settings.PAYTM_PAYMENT_GATEWAY_URL,
        'comany_name': settings.PAYTM_COMPANY_NAME,
        'data_dict': data_dict
    }
    return render(request, 'paytm-django-view.html', context)


@csrf_exempt
def response(request):
    resp = VerifyPaytmResponse(request)
    if resp['verified']:
        # save success details to db; details in resp['paytm']
        print(resp)
        order = Order.objects.get(user=resp['paytm']['CUST_ID'],ordered=False)
        order.ordered = True
        order.save()

        return HttpResponse("<center><h1>Transaction Successful</h1><center>", status=200)
    else:
        # check what happened; details in resp['paytm']
        return HttpResponse("<center><h1>Transaction Failed</h1><center>", status=400)