#from django.views import ListView
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from carts.models import Cart

from .models import Product
# Create your views here.

class ProductFeaturedListView(ListView):
	template_name = "products/list.html"

	def get_queryset(self,*args,**kwargs):
		request = self.request
		return Product.objects.all().featured()

class ProductFeaturedDetailView(DetailView):
	queryset = Product.objects.all().featured()
	template_name = "products/featured-detail.html"

	# def get_queryset(self,*args,**kwargs):
	# 	request = self.request
	# 	return Product.objects.featured()



#template for list all
class ProductListView(ListView):
	template_name = "products/list.html"

	def get_queryset(self,*args,**kwargs):
		request = self.request
		return Product.objects.all()


def product_list_view(request):
	#queryset = Product.objects.all()
	context={
	'object_list':queryset
	}
	return render(request, "products/list.html", context)


class ProductDetailSlugView(DetailView):
	queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
		
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_object(self, *args, **kwargs):
		request = self.request
		slug = self.kwargs.get('slug')
		try:
			instance = Product.objects.get(slug=slug, active = True)
		except Product.DoesNotExist: #no ID excpetion
			raise Http404('no product')
		except Product.MultipleObjectsReturned: #same slug exception
			qs = Product.objects.filter(slug = slug, active = True)
			instance = qs.first()
		except: #other problems
			raise Http404('uhhhhm')
		return instance





#template for details 
class ProductDetailView(DetailView):
	#queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args,**kwargs)
		print(context)
		return(context)

	def get_object(self,*args,**kwargs):
		request = self.request
		pk = self.kwargs.get(pk)
		instance = Product.objects.get_by_id(pk)
		if instance is None:
			raise Http404("Product does not exists")
		return instance

	# def get_queryset(self,*args,**kwargs):
	# 	request = self.request
	# 	pk = self.kwargs.get(pk)
	# 	return Product.objects.filter(pk=pk)


#choose item by id(pk)
def product_detail_view(request, pk=None, *args, **kwargs):
	#instance = Product.objects.get(pk=pk, featured = True)
	instance = Product.objects.get_by_id(pk)
	if instance is None:
		raise Http404("Product does not exists")
	# print(instance)
	# qs = Product.objects.filter(id=pk)
	# if qs.exists() and qs.count() == 1:
	# 	instance = qs.first()
	# else:
	# 	raise Http404("Product does not exists")



		#if instance is None:
		#raise Http404("product does not exist")




	#instance = Product.objects.get(pk=pk)
	#handles the error if there is 5 products and we're looking for id 5 it will show 404 page(without this funct there will be server error)
	#instance = get_object_or_404(Product, pk=pk)
	context={
	'object':instance
	}
	return render(request, "products/detail.html", context)
