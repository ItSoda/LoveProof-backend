from django.db import models

from users.models import User


class Post(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Пользователь'
    )
    header = models.CharField(max_length=100, verbose_name='Заголовок')
    text = models.TextField(max_length=1000, verbose_name='Текст')
    category = models.ForeignKey(
        to='Category',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return f'Post by {self.user}'

    def count_likes(self):
        return self.likes.count()

    def count_comments(self):
        return self.comments.count()


class Comment(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пользователь'
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    text = models.TextField(max_length=1000, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return f'Comment by {self.user}'

    def count_likes(self):
        return self.likes.count()

    def count_comments(self):
        return self.count


class Like(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пользователь'
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True,
        verbose_name='Пост'
    )
    comment = models.ForeignKey(
        to=Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True,
        verbose_name='Комментарий'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        if self.post:
            return f'Like by {self.user} on post {self.post.id}'
        elif self.comment:
            return f'Like by {self.user} on comment {self.comment.id}'


class Category(models.Model):
    title = models.CharField(max_length=25)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Report(models.Model):
    REPORT_TYPES_CHOICES= (
        ('post', 'Пост'),
        ('comment', 'Комментарий'),
    )
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('pending', 'На рассмотрении'),
        ('resolved', 'Рассмотрено'),
        ('rejected', 'Отклонено'),
        ('ignored', 'Игнорируется'),
        ('in_progress', 'В обработке'),
        ('closed', 'Закрыто'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='reports',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    reported_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPES_CHOICES,
        verbose_name='Тип жалобы'
    )
    reported_post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports',
        blank=True,
        null=True,
        verbose_name='Пост'
    )
    reported_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reports',
        blank=True, null=True,
        verbose_name='Комментарий'
    )
    text = models.TextField(verbose_name='Текст жалобы')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'

    def __str__(self):
        return f'Сomplaint from {self.user.username} about the {self.reported_type}'
