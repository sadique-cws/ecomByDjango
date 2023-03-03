from django.shortcuts import render,redirect,get_object_or_404
from shop.models import *
from django.contrib.auth.forms import AuthenticationForm
from  django.contrib.auth import authenticate, login as loginFun, logout
from shop.forms import RegisterForm
from django.contrib.auth.decorators import login_required

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
        
        return redirect(homepage)
    else:
        #need to create new order record
        order = Order.objects.create(user=r.user)
        order.items.add(order_item)
        # msg: this item is added to your cart
        return redirect(homepage)