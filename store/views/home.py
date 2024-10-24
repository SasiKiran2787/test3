from django.shortcuts import render , redirect , HttpResponseRedirect
from store.models.product import Product
from store.models.category import Category
from django.views import View


# Create your views here.
class Index(View):

    def post(self , request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product]  = quantity-1
                else:
                    cart[product]  = quantity+1

            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart' , request.session['cart'])
        return redirect('homepage')



    def get(self , request):
        # print()
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')

def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_all_products_by_categoryid(categoryID)
    else:
        products = Product.get_all_products();

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('you are : ', request.session.get('email'))
    return render(request, 'index.html', data)

from django.shortcuts import render, get_object_or_404, redirect
from store.models.product import Product
from store.models.category import Category
from django.views import View

# Product Detail View
class ProductDetail(View):

    def get(self, request, product_id):
        # Get the specific product
        product = get_object_or_404(Product, id=product_id)

        # Fetch recommended products based on category
        recommendations = Product.get_all_products_by_categoryid(product.category.id).exclude(id=product_id)[:4]

        context = {
            'product': product,
            'recommendations': recommendations,
            'categories': Category.objects.all(),
        }
        
        return render(request, 'product_detail.html', context)

    def post(self, request, product_id):
        # Handle adding the product to the cart
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})  # Fetch cart from session

        # Get the quantity from the form input (ensure it's at least 1)
        quantity = int(request.POST.get('quantity', 1))
        
        # Convert product_id to string for consistency in session key
        product_id_str = str(product_id)

        # If quantity is less than 1, set it to 1
        if quantity < 1:
            quantity = 1
        
        # If the product is already in the cart, update the quantity
        if product_id_str in cart:
            cart[product_id_str] += quantity  # Increment existing quantity
        else:
            cart[product_id_str] = quantity  # Set the selected quantity for the product

        # Save the updated cart back to session
        request.session['cart'] = cart
        
        # Redirect back to the same product detail page
        return redirect('product_detail', product_id=product.id)
