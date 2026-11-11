from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class Profile(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='profile/', blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, validators=[FileExtensionValidator(['pdf'])])
    social_links = models.JSONField(default=dict, blank=True, help_text='Object of names to HTTPS URLs. Example: {"Instagram": "https://instagram.com/yourname"}')
    available = models.BooleanField(default=True)
    location = models.CharField(max_length=100, default='Brooklyn, New York')
    email = models.EmailField(default='hello@example.com')
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Profile'

class Project(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    summary = models.CharField(max_length=300)
    case_study = models.TextField(help_text='Markdown supported. Raw HTML is sanitized.')
    client = models.CharField(max_length=160, blank=True)
    role = models.CharField(max_length=160)
    tech_stack = models.CharField(max_length=300, help_text='Comma-separated tags')
    live_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to='projects/', blank=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=80, default='Digital experience')
    year = models.PositiveIntegerField(default=2026)
    artwork = models.CharField(max_length=20, default='orbit', choices=[('orbit','Orbit'),('forma','Forma'),('aura','Aura'),('mono','Mono')])
    class Meta: ordering = ['display_order','-id']
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('project_detail', kwargs={'slug':self.slug})
    @property
    def tags(self): return [tag.strip() for tag in self.tech_stack.split(',') if tag.strip()]

class ProjectImage(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='gallery')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200,blank=True)
    display_order = models.PositiveIntegerField(default=0)
    class Meta: ordering=['display_order','id']
    def __str__(self): return self.caption or f'{self.project.title} image'

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=350)
    content = models.TextField(help_text='Markdown editor. HTML is sanitized on display.')
    cover_image = models.ImageField(upload_to='blog/', blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    published = models.BooleanField(default=False)
    tags = models.CharField(max_length=200,blank=True)
    class Meta: ordering=['-published_at']
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('post_detail',kwargs={'slug':self.slug})
    @property
    def reading_time(self): return max(1, round(len(self.content.split())/200))

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=160)
    budget = models.CharField(max_length=50,blank=True)
    message = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'{self.name}: {self.subject}'

class ContactThrottle(models.Model):
    """Database-backed, hashed-IP rate limiting shared across application workers."""
    key = models.CharField(max_length=64,unique=True)
    window_start = models.DateTimeField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)
