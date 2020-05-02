import math
import datetime
from django.db import models
from django.db.models.signals import pre_save, post_save

from django.db.models import Count,Sum,Avg

from django.utils import timezone


from billing.models import BillingProfile
from PickUp.utils import unique_order_id_generator

from carts.models import Cart

from addresses.models import Address

#creating tuple of status dropdown choises
ORDER_STATUS_CHOICES=(
	('created','Created'),
	('paid','Paid'),
	('shipped','Shipped'),
	('refunded','Refunded')
	)

class OrderManagerQuerySet(models.query.QuerySet):
	def recent(self):
		return self.order_by("-updated","-timestamp")
	def by_status(self,status='paid'):
		return self.filter(status=status)

	def get_sales_breakdown(self):
		# last orders by date and update(OrderManagerQS)
		recent=self.recent()
		#summing the total in the recent orders and finding  average of the order(OrderManagerQS)
		recent_data = recent.totals_data()
		#finding sum avg num of products in cart/products/price(OrderManagerQS)
		recent_cart_data = recent.cart_data()
		#check if the status is paid
		paid= recent.by_status(status='paid')

		paid_orders_data = paid.totals_data()

		data={
		'recent':recent,
		'recent_data':recent_data,
		'recent_cart_data':recent_cart_data,
		'paid':paid,
		'paid_orders_data':paid_orders_data
		}
		return data







		# counting weeks
	def by_weeks_range(self,weeks_ago=1, number_of_weeks=2):
		days_ago_start=weeks_ago * 7
		days_ago_end= days_ago_start - (number_of_weeks*7) 
			#now minus two weeks range
		start_date=timezone.now()-datetime.timedelta(days=days_ago_start)
		#now minus week
		end_date=timezone.now()-datetime.timedelta(days=days_ago_end)


		return self.by_range(start_date,end_date=end_date)


		#give a range using for todays sales
	def by_range(self, start_date, end_date=None):
		if end_date is None:
			return self.filter(updated__gte=start_date)
		return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

	def totals_data(self):
		return self.aggregate(
			Sum("total"),
			Avg("total")
			)

	def cart_data(self):
		return self.aggregate(
			Sum("cart__products__price"),
			Avg("cart__products__price"),
			Count("cart__products")
			)


class OrderManager(models.Manager):
	def get_queryset(self):
		return OrderManagerQuerySet(self.model, using=self._db)

	def new_or_get(self,billing_profile,cart_obj):
		created=False
		qs=self.get_queryset().filter(billing_profile=billing_profile,cart=cart_obj,status='created',active=True)
		if qs.count()==1:
			obj=qs.first()
		else:
			obj=self.model.objects.create(billing_profile=billing_profile,cart=cart_obj)
			created=True
		return obj,created

class Order(models.Model):
	order_id = models.CharField(max_length=120,blank=True)
	billing_profile = models.ForeignKey(BillingProfile,null=True, blank=True, on_delete=models.DO_NOTHING)
	shipping_address =models.ForeignKey(Address,related_name='shipping_adress' ,null=True, blank=True, on_delete=models.DO_NOTHING)
	billing_address =models.ForeignKey(Address,related_name='billing_adress' ,null=True, blank=True, on_delete=models.DO_NOTHING)
	cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING)
	status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
	shipping_total =models.DecimalField(default=3.50, max_digits=100, decimal_places=2)
	total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	active = models.BooleanField(default=True)
	updated = models.DateTimeField(auto_now=True)
	timestamp=models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.order_id

	objects = OrderManager()
		
	def update_total(self):
		cart_total = self.cart.total
		shipping_total = self.shipping_total
		new_total = math.fsum([cart_total, shipping_total])
		formatted_total = format(new_total, '.2f')
		self.total = formatted_total
		self.save()
		return new_total


	# function for finalizing
	def check_done(self):
		billing_profile = self.billing_profile
		shipping_address = self.shipping_address
		billing_address = self.billing_address
		total = self.total
		
		if billing_profile and shipping_address and billing_address and total>0:
			return True
		return False
	#function that changes status to paid(finalize checkout)
	def mark_paid(self):
		if self.check_done():
			self.status='paid'
			self.save()
		return self.status

#create random unique order id from utils.py
def pre_save_create_order_id(sender, instance, *args,**kwargs):
	if not instance.order_id:
		instance.order_id=unique_order_id_generator(instance)
	qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
	if qs.exists():
		qs.update(active=False)




#sending to the model
pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender,instance,created, *args,**kwargs):
	if not created:
		cart_obj = instance
		cart_total = cart_obj.total
		cart_id = cart_obj.id
		qs = Order.objects.filter(cart__id = cart_id)
		if qs.count() == 1:
			order_obj = qs.first()
			order_obj.update_total()

post_save.connect(post_save_cart_total, sender = Cart)

def post_save_order(sender,instance, created, *args, **kwargs):
	print('running')
	if created:
		print('updating')
		instance.update_total()
post_save.connect(post_save_order, sender = Order)