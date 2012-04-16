from django.shortcuts import render_to_response, HttpResponseRedirect
from django.http import HttpResponse
from django.template import RequestContext
from django.core.context_processors import csrf
from django.db.models import Q
from django.forms.util import ErrorList
from django.core.exceptions import PermissionDenied
from intranet.models import Member
from intranet.member_database.forms import NewMemberForm, EditMemberForm
import ldap


# Create your views here.
def main(request):
   return render_to_response('intranet/member_database/main.html',{"section":"intranet","page":'members'},context_instance=RequestContext(request))
  
def search(request):
   q = request.GET.get('q')
   if q:
      members = Member.objects.filter(Q(username__icontains=q) | \
                                    Q(first_name__icontains=q) | \
                                    Q(last_name__icontains=q)) \
                            .order_by('last_name', 'first_name')
   else:
      members = Member.objects.order_by('last_name', 'first_name')
  
   return render_to_response('intranet/member_database/search.html',{
    "section":"intranet",
    "page":'members',
    'members':members,
    'q':q},context_instance=RequestContext(request))
  
def new(request):
   if not request.user.is_top_4():
      raise PermissionDenied("You do not have rights to add new member.")
   c = {}
   if request.method == 'POST': # If the form has been submitted...
      form = NewMemberForm(request.POST) # A form bound to the POST data
      if form.is_valid(): # All validation rules pass
         try:
            form.save()
            return HttpResponseRedirect('/') # Redirect after POST
         except ValueError:
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(u"Not a valid netid")
          
   else:
      form = NewMemberForm() # An unbound form

   return render_to_response('intranet/member_database/form.html',{
      'form': form,
      "section":"intranet",
      "page":'members',
      "page_title":"Create new Member"
    },context_instance=RequestContext(request))
    
def edit(request,id):
   if not request.user.is_top_4():
      raise PermissionDenied("You do not have rights to edit member.")
   g = Member.objects.get(id=id)
   forms = EditMemberForm(instance=g)
   if request.method == 'POST': # If the form has been submitted...
      form = EditMemberForm(request.POST,instance=g) # A form bound to the POST data
      if form.is_valid(): # All validation rules pass
         form.save()
      return HttpResponseRedirect('/intranet/members') # Redirect after POST
   else:
      form = EditMemberForm(instance=g)

   return render_to_response('intranet/member_database/form.html',{
      "form":form,
      "section":"intranet",
      "page":'members',
      "page_title":"Edit member",
      },context_instance=RequestContext(request))