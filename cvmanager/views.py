from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.template.context import RequestContext
from cvmanager.models import CurriculumVitae

from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import *
from django.forms import *
from cvmanager.forms import CvForm
from django.core.exceptions import PermissionDenied


def render(request,template,context={}):
    return render_to_response(template,context,context_instance=RequestContext(request))

# General Views

def create_view(request,object_id,form_class,template_name):
    model = form_class.Meta.model
    u = get_object_or_404(User, username = object_id)
    
    if not request.user == u: raise PermissionDenied()
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            obj = form.save()
            if request.user.is_authenticated():
                request.user.message_set.create(message="The %s was updated" % model._meta.verbose_name )
            return HttpResponseRedirect(obj.get_absolute_url())
    else:
        form = form_class(initial={'owner':request.user.id})

    return render(request,template_name,{'form':form})


def edit_view(request,object_id,form_class,template_name):
    model = form_class.Meta.model
    u = get_object_or_404(User, username = object_id)
    
    if not request.user.username == u.username: raise PermissionDenied()
    
    obj = get_object_or_404(model, owner = u)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            
            obj = form.save()
            if request.user.is_authenticated():
                request.user.message_set.create(message="The %s was updated" % model._meta.verbose_name )
            return HttpResponseRedirect(obj.get_absolute_url())
    else:
        form = form_class(instance=obj)
    return render(request,template_name,{'form':form})



# Project Views

def curriculum(request,username):
    u = get_object_or_404(User, username = username)
    c = get_object_or_404(CurriculumVitae, owner = u)
    return render(request,'curriculum.html',{'u':u, 'cv':c})

@login_required
def curriculum_create(request,username):
    return create_view(request,username,CvForm,'curriculum_edit.html')

    
@login_required
def curriculum_edit(request,username):
    return edit_view(request,username,CvForm,'curriculum_edit.html')
