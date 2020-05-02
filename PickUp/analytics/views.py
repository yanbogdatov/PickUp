
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.db.models import Count, Sum, Avg


from django.views.generic import TemplateView, View

from django.utils import timezone
import datetime
import random

from orders.models import Order

#staff for chart
class SalesAjaxView(View):
	#send data to chart if user is staff
	def get(self,request,*args,**kwargs):

		data={}
		if request.user.is_staff:
			qs = Order.objects.all().by_weeks_range(weeks_ago=5,number_of_weeks=5)
			if request.GET.get('type')=='week':
				days = 7
				#last item is today and it goes -1 each loop
				start_date=timezone.now().today() - datetime.timedelta(days=days-1)
				datetime_list = []
				labels=[]
				salesItmes=[]
				#loop goes through start date(first substract 0) and go to num of days

				for x in range(0,days):
					new_time =start_date+datetime.timedelta(days=x)
					datetime_list.append(
							new_time
						
						)
					labels.append(
						new_time.strftime("%a") #reformat the date function to dates
						)
					new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
					day_total= new_qs.totals_data()['total__sum']
					if day_total is None:
						day_total=0
					salesItmes.append(
							day_total
						)


				data['labels'] = labels
				data['data'] = salesItmes
				if request.GET.get('type')=='4weeks':
					data['labels'] = ["Four weeks ago","Three weeks ago","Two weeks ago","Last week"]
					

					data['data'] = [2,7,6,9]

		return JsonResponse(data)




class SalesView(TemplateView):
	template_name = 'analytics/sales.html'





	def dispatch(self,*args,**kwargs):
		user=self.request.user
		#check if user is admin or give him 401 page - not allowed
		if not user.is_staff:
			return HttpResponse("not allowed", status=401)
		return super(SalesView,self).dispatch(*args,**kwargs)




	def get_context_data(self,*args,**kwargs):
		context = super(SalesView, self).get_context_data(*args,**kwargs)
		#getting list of all of the orders
		qs = Order.objects.all().by_weeks_range(weeks_ago=10,number_of_weeks=10)


		#filtering qs by date, and get all the data(total etc.)
		context['today'] = qs.by_range(start_date=timezone.now().date()).get_sales_breakdown()
		context['this_week']= qs.by_weeks_range(weeks_ago=1,number_of_weeks=1).get_sales_breakdown()
		context['four_weeks']= qs.by_weeks_range(weeks_ago=5,number_of_weeks=4).get_sales_breakdown()



		return context