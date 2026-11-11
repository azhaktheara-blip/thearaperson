import json
import logging
from datetime import timedelta
import bleach
import markdown
from django.conf import settings
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import Project, BlogPost, ContactThrottle
from .forms import ContactForm
logger = logging.getLogger(__name__)

def rich_text(value):
    return bleach.clean(markdown.markdown(value, extensions=['fenced_code','tables']),
        tags=['p','br','strong','em','h2','h3','h4','ul','ol','li','blockquote','a','code','pre','hr','table','thead','tbody','tr','th','td'],
        attributes={'a':['href','title']}, protocols=['https','http','mailto'], strip=True)

@method_decorator(ensure_csrf_cookie,name='dispatch')
class HomeView(ListView):
    model=Project
    template_name='portfolio/index.html'
    context_object_name='projects'
    def get_queryset(self): return Project.objects.filter(featured=True)[:6]
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['posts']=BlogPost.objects.filter(published=True,published_at__lte=timezone.now())[:3]
        return context

class PortfolioView(ListView):
    model=Project
    template_name='portfolio/project_list.html'
    context_object_name='projects'
    paginate_by=12
    def get_queryset(self):
        qs=super().get_queryset()
        category=self.request.GET.get('category','')
        return qs.filter(category=category) if category else qs
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['categories']=Project.objects.order_by('category').values_list('category',flat=True).distinct()
        return context

class ProjectDetailView(DetailView):
    model=Project
    template_name='portfolio/project_detail.html'
    context_object_name='project'
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['case_study']=rich_text(self.object.case_study)
        context['related_projects']=Project.objects.exclude(pk=self.object.pk)[:3]
        return context

class BlogListView(ListView):
    template_name='portfolio/blog_list.html'
    context_object_name='posts'
    paginate_by=6
    def get_queryset(self): return BlogPost.objects.filter(published=True,published_at__lte=timezone.now())

class PostDetailView(DetailView):
    template_name='portfolio/post_detail.html'
    context_object_name='post'
    def get_queryset(self): return BlogPost.objects.filter(published=True,published_at__lte=timezone.now())
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['article']=rich_text(self.object.content)
        return context

class AboutView(TemplateView): template_name='portfolio/about.html'
@method_decorator(ensure_csrf_cookie,name='dispatch')
class ContactView(TemplateView): template_name='portfolio/contact.html'

def not_found(request,exception=None): return render(request,'404.html',status=404)

def csrf_failure(request,reason=''):
    if request.path=='/api/contact/':
        return JsonResponse({'ok':False,'message':'Your session expired. Refresh this page and try again.'},status=403)
    return render(request,'403.html',status=403)

@require_POST
def contact_api(request):
    if request.content_type != 'application/json':
        return JsonResponse({'ok':False,'message':'Use application/json.'},status=415)
    try:
        data=json.loads(request.body)
    except (ValueError,UnicodeDecodeError):
        return JsonResponse({'ok':False,'message':'Invalid JSON.'},status=400)
    if not isinstance(data,dict):
        return JsonResponse({'ok':False,'message':'Expected a JSON object.'},status=400)
    if any(not isinstance(value,str) for value in data.values()):
        return JsonResponse({'ok':False,'message':'Form values must be text.'},status=400)
    form=ContactForm(data)
    if not form.is_valid():
        return JsonResponse({'ok':False,'message':'Please check the highlighted fields.','errors':form.errors.get_json_data()},status=400)
    if form.cleaned_data.get('website'):
        return JsonResponse({'ok':True,'message':'Thank you. Your message has been received.'})
    # Never trust arbitrary forwarding headers. REMOTE_ADDR must be set by the trusted deployment proxy.
    key=salted_hmac('contact-rate-limit', request.META.get('REMOTE_ADDR','unknown')).hexdigest()
    try:
        with transaction.atomic():
            row,_=ContactThrottle.objects.get_or_create(key=key)
            row=ContactThrottle.objects.select_for_update().get(pk=row.pk)
            if timezone.now()-row.window_start>timedelta(hours=1):
                row.window_start=timezone.now();row.count=0
            if row.count>=settings.CONTACT_RATE_LIMIT:
                response=JsonResponse({'ok':False,'message':'Too many messages. Please try again in an hour.'},status=429)
                response['Retry-After']='3600'
                return response
            row.count+=1;row.save(update_fields=['window_start','count'])
            form.save()
    except DatabaseError:
        logger.exception('Contact message persistence failed')
        return JsonResponse({'ok':False,'message':'Unable to save your message. Please try again later.'},status=503)
    return JsonResponse({'ok':True,'message':'Message received. Thanks for reaching out — I’ll be in touch soon.'},status=201)
