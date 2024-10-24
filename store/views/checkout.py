import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from store.models.product import Product
from store.models.orders import Order
from store.models.customer import Customer
import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, get_object_or_404
# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})
class CheckOut(View):
    def post(self, request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))

        # Total cart price
        total_price = sum(product.price * cart.get(str(product.id), 0) for product in products)

        # Handle PayPal Online Payment
        if payment_method == "online":
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": request.build_absolute_uri('/payment-success'),
                    "cancel_url": request.build_absolute_uri('/payment-cancel')
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": product.name,
                            "sku": product.id,
                            "price": str(product.price),
                            "currency": "USD",
                            "quantity": cart.get(str(product.id), 1)
                        } for product in products]
                    },
                    "amount": {
                        "total": str(total_price),
                        "currency": "USD"
                    },
                    "description": "Payment for order"
                }]
            })

            # Create payment and log the details
            if payment.create():
                approval_url = next((str(link.href) for link in payment.links if link.rel == "approval_url"), None)
                if approval_url:
                    # Store order details in session before redirecting to PayPal
                    request.session['order_address'] = address
                    request.session['order_phone'] = phone
                    request.session['payment_method'] = payment_method  # Store payment method
                    return redirect(approval_url)  # Redirect user to PayPal
            else:
                logging.error(f"PayPal payment creation failed: {payment.error}")
                return JsonResponse({"error": payment.error}, status=400)

        # Handle Cash on Delivery (COD)
        for product in products:
            order = Order(
                customer=Customer(id=customer),
                product=product,
                price=product.price,
                address=address,
                phone=phone,
                quantity=cart.get(str(product.id), 1),
                payment_method=payment_method  # Save payment method as "COD"
            )
            order.place_order()

        # Clear the cart after creating the orders
        request.session['cart'] = {}
        return redirect('cart')
def payment_success(request):
    # Retrieve address, phone, and payment method from the session
    address = request.session.get('order_address')
    phone = request.session.get('order_phone')
    payment_method = request.session.get('payment_method', 'online')  # Default to "online" for PayPal

    # Get the cart data
    cart = request.session.get('cart', {})
    products = []
    total_amount = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)  # Fetch the product from the database
        products.append(product)
        total_amount += product.price * quantity  # Make sure product.price is a float or Decimal

    # Place orders after confirming successful payment
    customer = request.session.get('customer')
    for product in products:
        order = Order(
            customer=Customer(id=customer),
            product=product,
            price=product.price,
            address=address,
            phone=phone,
            quantity=cart.get(str(product.id), 1),
            payment_method=payment_method,
            paid=(payment_method == 'online')  # Set paid to True if payment method is online
        )
        order.place_order()

    # Clear the cart and session data after placing orders
    request.session['cart'] = {}
    request.session['order_address'] = None
    request.session['order_phone'] = None
    request.session['payment_method'] = None

    context = {
        'message': 'Payment was successful!',
        'products': products,
        'cart': {},  # Clear the cart in the template
        'total_amount': total_amount,
    }
    return render(request, 'payment_success.html', context)
