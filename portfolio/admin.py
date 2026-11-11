from django.contrib import admin
from .models import Profile,Project,ProjectImage,BlogPost,ContactMessage
class GalleryInline(admin.TabularInline):
    model=ProjectImage
    extra=1
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display=['title','category','featured','display_order']
    list_editable=['featured','display_order']
    list_filter=['featured','category']
    search_fields=['title','summary','client']
    prepopulated_fields={'slug':('title',)}
    inlines=[GalleryInline]
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display=['title','published','published_at']
    list_filter=['published','published_at']
    search_fields=['title','content','tags']
    prepopulated_fields={'slug':('title',)}
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['name','email','available']
    def has_add_permission(self,request):
        return not Profile.objects.exists() and super().has_add_permission(request)
@admin.action(description='Mark selected messages as read')
def mark_read(modeladmin,request,queryset): queryset.update(is_read=True)
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display=['name','email','subject','budget','created_at','is_read']
    list_filter=['is_read','created_at']
    search_fields=['name','email','subject','message']
    readonly_fields=['name','email','subject','budget','message','created_at']
    actions=[mark_read]
    def has_add_permission(self,request): return False
@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display=['project','caption','display_order']
admin.site.site_header='Alex Morgan — Studio'
admin.site.site_title='Portfolio studio'
