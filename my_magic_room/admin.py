from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from django.shortcuts import redirect
from my_magic_room.models import achivments, memes, stories, tales, posts, krissy_blog
from my_magic_room.forms import MemesAdminForm, TalesAdminForm, JournalPageAdminForm
from my_magic_room.forms import StoriesAdminForm, PostsAdminForm, CrissyBlogAdminForm


class MemesAdmin(admin.ModelAdmin):
    form = MemesAdminForm
    exclude = ('slug',)  # Исключаем поле slug из формы редактирования

    def render_change_form(self, request, context, *args, **kwargs):
        # Получаем объект и генерируем URL для предпросмотра
        obj = kwargs.get("obj")
        if obj and obj.slug:
            preview_url = reverse('meme_detail', args=[obj.slug])
            context["preview_url"] = preview_url
        return super().render_change_form(request, context, *args, **kwargs)
    
    class Media:
        css = {
            'all': ('css/quill-patch.css', 'css/custom-admin.css')  # Подключаем ваш файл стилей
        }
        js = ()  # Если нужно подключить кастомный JavaScript


class TalesAdmin(admin.ModelAdmin):
    form = TalesAdminForm
    exclude = ('slug',)

    def render_change_form(self, request, context, *args, **kwargs):
        # Получаем объект и генерируем URL для предпросмотра
        obj = kwargs.get("obj")
        if obj and obj.slug:
            # Генерация URL для предпросмотра на основе slug
            preview_url = reverse('tale_detail', args=[obj.slug])
            # Добавление кнопки предпросмотра в контекст
            context["preview_url"] = preview_url
        else:
            context['preview_url'] = None    

        return super().render_change_form(request, context, *args, **kwargs)

    # Указываем шаблон для отображения формы редактирования
    change_form_template = 'admin/change_form_for_tales.html'

    class Media:
        css = {
            'all': ('css/quill-patch.css', 'css/custom-admin.css')
        }
        js = ('js/admin_preview.js',)




class StoriesAdmin(admin.ModelAdmin):
    form = StoriesAdminForm
    exclude = ('slug',)  # Исключаем поле slug из формы редактирования

    def render_change_form(self, request, context, *args, **kwargs):
        obj = kwargs.get('obj')
        if obj and obj.slug:
            # Генерация URL для предпросмотра
            preview_url = reverse('storie_detail', args=[obj.slug])
            context['preview_url'] = preview_url
        return super().render_change_form(request, context, *args, **kwargs)

    
    class Media:
        css = {
            'all': ('css/quill-patch.css', 'css/custom-admin.css')  # Подключаем ваш файл стилей
        }
        js = ()  # Если нужно подключить кастомный JavaScript


class PostsAdmin(admin.ModelAdmin):
    form = PostsAdminForm
    exclude = ('slug',)  # Исключаем поле slug из формы редактирования
    
    def render_change_form(self, request, context, *args, **kwargs):
        preview_url = reverse('preview_post')
        context["preview_url"] = preview_url
        return super().render_change_form(request, context, *args, **kwargs)
    
    def response_change(self, request, obj):
        """Перенаправление после редактирования и сохранения поста"""
        # Проверяем, нажата ли кнопка "Сохранить"
        if ("_save" in request.POST) or ("_save0" in request.POST):
            # Перенаправляем на нужную страницу (например, на просмотр поста)
            # return redirect(reverse('post_detail', kwargs={'slug': obj.slug}))
            return redirect(reverse('posts_list'))

        return super().response_change(request, obj)  # Обычное поведение
    
    def response_add(self, request, obj, post_url_continue=None):
        """Перенаправление после добавления поста"""
        # return redirect(reverse('post_detail', kwargs={'slug': obj.slug}))
        return redirect(reverse('posts_list'))
    
    def response_delete(self, request, obj_display, obj_id):
        """Перенаправление после удаления поста"""
        return redirect(reverse('posts_list'))  # Замените 'posts_list' на свой URL-нейм

    # Указываем шаблон для отображения формы редактирования
    change_form_template = 'admin/change_form_for_posts.html'
    
    class Media:
        css = {
            'all': ('css/ckeditor5-custom.css', 'css/custom-admin.css')  # Подключаем ваш файл стилей
        }
        js = ('js/admin_preview.js','js/custom-admin.js')  # Если нужно подключить кастомный JavaScript


class CrissyBlogAdmin(admin.ModelAdmin):
    form = CrissyBlogAdminForm
    exclude = ('slug',)  # Исключаем поле slug из формы редактирования

    def render_change_form(self, request, context, *args, **kwargs):
        preview_url = reverse('preview_post')
        context["preview_url"] = preview_url
        return super().render_change_form(request, context, *args, **kwargs)

    def response_change(self, request, obj):
        """Перенаправление после редактирования и сохранения объекта"""
        # Проверяем, нажата ли кнопка "Сохранить"
        if ("_save" in request.POST) or ("_save0" in request.POST):
            # Перенаправляем на нужную страницу 
            return redirect(reverse('krissy_blog_list'))
        
        return super().response_change(request, obj)  # Обычное поведение
        
    def response_add(self, request, obj, post_url_continue=None):
        """Перенаправление после добавления объекта"""
        return redirect(reverse('krissy_blog_list'))  

    def response_delete(self, request, obj_display, obj_id):
        """Перенаправление после удаления объекта"""
        return redirect(reverse('krissy_blog_list'))   
    
    # Указываем шаблон для отображения формы редактирования
    change_form_template = 'admin/change_form_for_posts.html'
    
    class Media:
        css = {
            'all': ('css/ckeditor5-custom.css', 'css/custom-admin.css')  # Подключаем ваш файл стилей
        }
        js = ('js/admin_preview.js','js/custom-admin.js')  # Если нужно подключить кастомный JavaScript


class JournalPageAdmin(admin.ModelAdmin):
    form = JournalPageAdminForm


admin.site.register(achivments)
admin.site.register(memes, MemesAdmin)
admin.site.register(stories, StoriesAdmin)
admin.site.register(tales, TalesAdmin)
admin.site.register(posts, PostsAdmin)
admin.site.register(krissy_blog, CrissyBlogAdmin)