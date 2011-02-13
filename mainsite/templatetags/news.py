from django.template import Library
from mainsite.models import News
from accounts.models import UserProfile
from cvmanager.models import CurriculumVitae
from mainsite.utils import translate

register = Library()

@register.simple_tag
def latest_news(number = 5):
	latest = News.objects.filter(is_published=True).order_by('-date')[:number]
	
	html = "<ul>\n"
	for obj in latest:
		html += "<li class='archive'><a href='%s'>%s</a></li>\n" %(obj.get_absolute_url(), obj.title)
	
	if number and News.objects.filter(is_published=True).count() > number:
		html += "<li><a href='/noticias/arquivo/' title='Arquivo'>...</a></li>"
	
	html += "</ul>"
	return html

@register.simple_tag
def load_archive(number = 0):
	date_list = News.objects.filter(is_published=True).dates('date', 'month')[::-1]
	
	if number: date_list = date_list[:number]
	
	html = "<ul>\n"
	for obj in date_list:
		html += "<li><a href='/noticias/arquivo/%s'>%s</a></li>\n" %(obj.strftime('%Y/%m/'), " ".join( map( translate, obj.strftime('%B %Y').split() ) ))
	
	if number and News.objects.filter(is_published=True).count() > number:
		html += "<li><a href='/noticias/arquivo/' title='Arquivo'>...</a></li>"
	
	html += "</ul>"
	return html

@register.filter
def trans_month(string):
	return " ".join( map( translate, string.split() ) )
	
@register.simple_tag
def author_link(author):
	url = None
	
	# Fetch auxiliar Models
	
	try: profile = author.get_profile()
	except UserProfile.DoesNotExist: profile = None
	
	if author.curriculumvitae_set.count(): cv = CurriculumVitae.objects.get(owner=author)
	else: cv = None
	
	# Build the url
	
	if profile:
		url = ((profile.homepage if profile else None) or (cv.homepage if cv else None)) or (('http://twitter.com/'+profile.twitter) if profile.twitter else None) or profile.facebook
	
	elif cv and not profile:
		url = cv.homepage
	
	# Build the html
	
	if url: return '<a href="%s">%s</a>' % (url, author.get_full_name())
	else:   return author.get_full_name()