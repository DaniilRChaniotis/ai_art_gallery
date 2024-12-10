from django.shortcuts import render, get_object_or_404, redirect
from .models import Art, Cart, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from decimal import Decimal
from django.contrib import messages
from .forms import ContactForm
from django.template.loader import get_template


stripe.api_key = settings.STRIPE_SECRET_KEY


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'gallery/register.html', {'form': form})


def home(request):
    arts = Art.objects.all()
    return render(request, 'gallery/home.html', {'arts': arts})


def art_detail(request, art_id):
    art = get_object_or_404(Art, id=art_id)
    return render(request, 'gallery/art_detail.html', {'art': art})


@login_required
def add_to_cart(request, art_id):
    art = get_object_or_404(Art, id=art_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the art is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, art=art)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def subtract_from_cart(request, art_id):
    art = get_object_or_404(Art, id=art_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item = CartItem.objects.filter(cart=cart, art=art).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    # Calculate the total price
    total_price = sum(item.art.price * item.quantity for item in items)

    return render(request, 'gallery/cart.html', {'cart': cart, 'items': items, 'total_price': total_price})


def checkout(request):
    if request.method == 'POST':
        try:
            amount = request.POST.get('amount', '0')
            amount = Decimal(amount) * 100  # Convert to cents
            amount = int(amount)

            if amount <= 0:
                raise ValueError("Invalid amount for payment.")

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Artwork Purchase',
                            },
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',
                cancel_url='http://127.0.0.1:8000/cancel/',
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return render(request, 'gallery/checkout_error.html', {'error': str(e)})

    return render(request, 'gallery/checkout.html', {'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})


def success(request):
    return render(request, 'gallery/success.html')


def cancel(request):
    return render(request, 'gallery/cancel.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'gallery/contact.html', {'form': form})



@login_required
def dashboard(request):
    orders = request.user.orders.all() if hasattr(request.user, 'orders') else []
    favorites = request.user.favorites.all() if hasattr(request.user, 'favorites') else []

    # Debug output
    print("Orders:", orders)
    print("Favorites:", favorites)

    return render(request, 'gallery/dashboard.html', {
        'orders': orders,
        'favorites': favorites,
        'user': request.user,
    })

