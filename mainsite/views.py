from mainsite.models import News
from mainsite.forms import NewsForm, SearchNewsForm

from django.contrib.auth.decorators import login_required
from common.utils import render
from django.shortcuts import get_object_or_404
from common.views import PermissionDenied

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseForbidden

from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.date_based import archive_index

from django.db.models import Q

# News Views

@login_required
def create_news(request):
	if request.user.has_perm('mainsite.add_news'):
	
		if request.method == 'POST':
			form = NewsForm(request.POST)

			if form.is_valid():
				obj = form.save()

				request.user.message_set.create(message="News Created")

				return HttpResponseRedirect(obj.get_absolute_url())
		else:
			form = NewsForm()
		return render(request,"news_edit.html",{'form':form})

	else:
		return PermissionDenied(request)

def archive(request):
	date_list = News.objects.filter(is_published=True).dates('date', 'year')[::-1]

	return render(request,'news_archive.html', { 'date_list': date_list })
	
def news_detail(request, **kwargs):
	if (request.user.has_perm('mainsite.change_news')):
		kwargs['queryset'] = News.objects.all()
	else: kwargs['queryset'] = News.objects.filter(is_published=True)
	
	return object_detail(request, **kwargs)
		
def news_index(request, **kwargs):
	if (request.user.has_perm('mainsite.change_news')):
		kwargs['queryset'] = News.objects.all().order_by('-date')
	else:
		kwargs['queryset'] = News.objects.filter(is_published=True).order_by('-date')
	
	kwargs.pop('date_field')
	kwargs['paginate_by'] = 3
	return object_list(request, **kwargs)

def search_news(request):
	
	# Compare function used to sort the results array.
	def cmp_news(x, y):
		if x.date < y.date: return 1
		elif x.date == y.date: return 0
		else: return -1
	
	res = None
	search_term = ''
	
	if request.method == 'GET' and request.GET.has_key('q'):
		form = SearchNewsForm(request.GET)
		
		if form.is_valid():
			search_term = form.cleaned_data['q'].rstrip()
			
			if request.user.has_perm('mainsite.change_news'):
				queryset = News.objects.all()
			else: queryset = News.objects.filter(is_published=True)
			
			for word in search_term.split(' '):
				if res == None: res = set(queryset.filter(Q(title__icontains=word)\
														| Q(body__icontains=word)))
				else: res = res & set(queryset.filter(Q(title__icontains=word)\
													| Q(body__icontains=word)))
			res = sorted(list(res), cmp_news)
	else:
		form = SearchNewsForm()
	
	return render(request,'news_search.html',{'search_term': search_term, 'results': res})