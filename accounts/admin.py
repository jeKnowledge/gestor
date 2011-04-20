from accounts.models import UserProfile
from django.contrib import admin

from accounts.forms import UserProfileAdminForm

class UserProfileAdmin(admin.ModelAdmin):	
	list_display = ('user','organization')	
	list_filter = ('organization',)
	search_fields = ('user__first_name','user__last_name','user__username','title')
	
	form = UserProfileAdminForm
	

admin.site.register(UserProfile,UserProfileAdmin)
