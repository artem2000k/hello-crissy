from django.contrib.auth import get_user_model
from django.db import models
from django_quill.fields import QuillField
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
# from hsweb import settings


# Create your models here.
class achivments(models.Model):
    name = models.CharField('Название', max_length=100)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    def __str__(self):
        return self.name or 'Unnamed'
    class Meta:
        verbose_name = 'Награда'
        verbose_name_plural = 'Награды'


class memes(models.Model):
    title = models.CharField('Название',max_length=255)
    anonce = models.TextField('Анонс',default='', blank=True)
    image = models.ImageField('Обложка', upload_to='memes/', blank=True)
    description = QuillField()
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.title or 'Unnamed'

    class Meta:
        verbose_name = 'Мем'
        verbose_name_plural = 'Мемы'

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = slugify(self.id)
        super().save(*args, **kwargs)


class tales(models.Model):
    title = models.CharField('Название', max_length=255)
    anonce = models.TextField('Анонс', default='', blank=True)
    image = models.ImageField(upload_to='tales/', blank=True)
    # description = QuillField()
    description = CKEditor5Field(config_name='default')
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Рассказ'
        verbose_name_plural = 'Рассказы'

    def __str__(self):
        return self.title or 'Unnamed'

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = slugify(self.id)
        super().save(*args, **kwargs)


class stories(models.Model):
    title = models.CharField('Название',max_length=255)
    anonce = models.TextField('Анонс', default='', blank=True)
    image = models.ImageField(upload_to='stories/', blank=True)
    description = QuillField()
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    slug = models.SlugField(null=True, max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'Истории'

    def __str__(self):
        return self.title or 'Unnamed'

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = slugify(self.id)
        super().save(*args, **kwargs)


class posts(models.Model):
    title = models.CharField('Название',max_length=255)
    anonce = models.TextField('Анонс',default='', blank=True)
    image = models.ImageField('Обложка', upload_to='posts/', blank=True)
    description = CKEditor5Field('Текст', config_name='default')
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.title or 'Unnamed'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = slugify(self.id)
        super().save(*args, **kwargs)


class krissy_blog(models.Model):
    title = models.CharField('Название',max_length=255)
    anonce = models.TextField('Анонс',default='', blank=True)
    image = models.ImageField(upload_to='crissy_blog/', blank=True)
    description = CKEditor5Field('Текст', config_name='default')
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.title or 'Unnamed'

    class Meta:
        verbose_name = 'Крисси блог'
        verbose_name_plural = 'Крисси блог'

    def save(self, *args, **kwargs):
        if not self.slug:
            super().save(*args, **kwargs)
            self.slug = slugify(self.id)
        super().save(*args, **kwargs)


class Journal(models.Model):
    #тут не get_user_model потому, что иначе ошибка. Джанго момент походу
    user = models.ForeignKey('user_management.user', on_delete=models.CASCADE, related_name='journals')
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    updated_at = models.DateTimeField('Изменен',auto_now=True)
    
    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'


class JournalPage(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField('Заголовок',max_length=255, blank=True, null=True)
    content = QuillField('Текст')
    page_number = models.PositiveIntegerField('Номер страницы')
    created_at = models.DateTimeField('Создан',auto_now_add=True)
    updated_at = models.DateTimeField('Изменен',auto_now=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('journal', 'page_number')
        verbose_name = 'Страница журнала'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return f"{self.title} - Page {self.page_number}"
