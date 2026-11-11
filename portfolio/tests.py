import json
from datetime import timedelta
from io import StringIO
from unittest.mock import patch
from django.test import TestCase,Client,override_settings
from django.core.management import call_command
from django.db import DatabaseError
from django.utils import timezone
from .models import Profile,Project,BlogPost,ContactMessage,ContactThrottle
from .views import rich_text

class PagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo',stdout=StringIO())
    def test_public_pages_render(self):
        for path in ['/','/work/','/about/','/journal/','/contact/','/work/orbit/','/journal/design-that-feels-like-something/']:
            with self.subTest(path=path):
                response=self.client.get(path)
                self.assertEqual(response.status_code,200)
                self.assertContains(response,'Skip to content')
    def test_demo_is_idempotent_and_preserves_edits(self):
        profile=Profile.objects.first();profile.name='My edited name';profile.save()
        call_command('seed_demo',stdout=StringIO())
        self.assertEqual(Project.objects.count(),4)
        self.assertEqual(Profile.objects.get().name,'My edited name')
        self.assertEqual(BlogPost.objects.count(),3)
    def test_category_filter(self):
        response=self.client.get('/work/',{'category':'Brand identity'})
        self.assertContains(response,'Orbit®')
        self.assertNotContains(response,'Forma Living')
    def test_hidden_and_future_articles_are_not_public(self):
        for slug,published,date in [('draft',False,timezone.now()),('future',True,timezone.now()+timedelta(days=1))]:
            BlogPost.objects.create(title='Hidden sentinel',slug=slug,excerpt='Hidden excerpt',content='Hidden',published=published,published_at=date)
            self.assertEqual(self.client.get(f'/journal/{slug}/').status_code,404)
        self.assertNotContains(self.client.get('/journal/'),'Hidden sentinel')
    def test_unknown_project_is_404(self):
        self.assertEqual(self.client.get('/work/missing/').status_code,404)
    @override_settings(DEBUG=False,SECURE_SSL_REDIRECT=False)
    def test_custom_404(self):
        response=self.client.get('/this-does-not-exist/')
        self.assertEqual(response.status_code,404)
        self.assertContains(response,'This page went',status_code=404)
    def test_markdown_sanitizes_html_and_unsafe_links(self):
        result=rich_text('## Safe heading\n\n<script>alert(1)</script>\n\n[link](javascript:alert(2))\n\n<img src=x onerror=alert(3)>')
        self.assertIn('<h2>Safe heading</h2>',result)
        self.assertNotIn('<script',result)
        self.assertNotIn('href="javascript:',result)
        self.assertNotIn('<img',result)
    def test_empty_site_renders(self):
        Project.objects.all().delete();BlogPost.objects.all().delete();Profile.objects.all().delete()
        self.assertEqual(self.client.get('/').status_code,200)

class ContactTests(TestCase):
    def setUp(self):
        self.client=Client(enforce_csrf_checks=True)
        self.client.get('/contact/')
        self.csrf=self.client.cookies['csrftoken'].value
        self.payload={'name':'Jamie Taylor','email':'jamie@example.com','subject':'A portfolio website','budget':'$5,000 – $10,000','message':'I would love to discuss a new portfolio project with you.','website':''}
    def submit(self,payload=None,**kwargs):
        return self.client.post('/api/contact/',json.dumps(payload if payload is not None else self.payload),content_type='application/json',HTTP_X_CSRFTOKEN=self.csrf,**kwargs)
    def test_valid_message_is_persisted(self):
        response=self.submit()
        self.assertEqual(response.status_code,201)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(ContactMessage.objects.get().email,'jamie@example.com')
    def test_csrf_required(self):
        response=Client(enforce_csrf_checks=True).post('/api/contact/',json.dumps(self.payload),content_type='application/json')
        self.assertEqual(response.status_code,403)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(ContactMessage.objects.count(),0)
    def test_field_validation(self):
        for update,field in [({'email':'invalid'},'email'),({'message':'short'},'message'),({'name':' '},'name'),({'subject':''},'subject'),({'message':'x'*5001},'message')]:
            with self.subTest(field=field):
                response=self.submit({**self.payload,**update})
                self.assertEqual(response.status_code,400)
                self.assertIn(field,response.json()['errors'])
        self.assertEqual(ContactMessage.objects.count(),0)
    def test_malformed_json(self):
        response=self.client.post('/api/contact/','{broken',content_type='application/json',HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(response.status_code,400)
    def test_json_object_and_string_values_required(self):
        for value in [[],None,{'name':5},{'email':{'nested':'bad'}}]:
            response=self.client.post('/api/contact/',json.dumps(value),content_type='application/json',HTTP_X_CSRFTOKEN=self.csrf)
            self.assertEqual(response.status_code,400)
    def test_post_only_and_content_type(self):
        self.assertEqual(self.client.get('/api/contact/').status_code,405)
        response=self.client.post('/api/contact/',self.payload,HTTP_X_CSRFTOKEN=self.csrf)
        self.assertEqual(response.status_code,415)
    def test_honeypot_does_not_save(self):
        response=self.submit({**self.payload,'website':'https://spam.example'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(ContactMessage.objects.count(),0)
    @override_settings(CONTACT_RATE_LIMIT=2)
    def test_rate_limit_and_window_reset(self):
        self.assertEqual(self.submit().status_code,201)
        self.assertEqual(self.submit().status_code,201)
        response=self.submit()
        self.assertEqual(response.status_code,429)
        self.assertEqual(response['Retry-After'],'3600')
        self.assertEqual(ContactMessage.objects.count(),2)
        ContactThrottle.objects.update(window_start=timezone.now()-timedelta(hours=2))
        self.assertEqual(self.submit().status_code,201)
    @override_settings(CONTACT_RATE_LIMIT=1)
    def test_spoofed_forwarded_ip_does_not_bypass_limit(self):
        self.assertEqual(self.submit(HTTP_X_FORWARDED_FOR='1.1.1.1').status_code,201)
        self.assertEqual(self.submit(HTTP_X_FORWARDED_FOR='2.2.2.2').status_code,429)
    @patch('portfolio.forms.ContactForm.save',side_effect=DatabaseError('offline'))
    def test_persistence_failure_returns_json_and_rolls_back(self,mock_save):
        with self.assertLogs('portfolio.views',level='ERROR'):
            response=self.submit()
        self.assertEqual(response.status_code,503)
        self.assertFalse(response.json()['ok'])
        self.assertEqual(ContactThrottle.objects.count(),0)
