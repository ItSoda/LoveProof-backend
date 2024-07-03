from rest_framework import serializers

from community.models import Post, Comment, Category, Report


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Поля:
    - id: id категории.
    - title: Название категории.
    """
    class Meta:
        model = Category
        fields = ('id', 'title')


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.

    Поля:
    - id: id комментария.
    - user: Пользователь, оставивший комментарий.
    - text: Текст комментария.
    - created_at: Дата и время создания комментария.
    """
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'text', 'created_at', 'likes_count')
        read_only_fields = ('id', 'user', 'created_at', 'likes_count')

    def get_likes_count(self, obj):
        return obj.likes.count()


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Post.

    Поля:
    - id: id поста.
    - user: Пользователь, создавший пост.
    - header: Заголовок поста.
    - text: Текст поста.
    - category: Категория поста (вложенный сериализатор CategorySerializer).
    - created_at: Дата и время создания поста.
    - comments_count: Количество комментариев под постом (вычисляемое поле).
    - likes_count: Количество лайков под постом (вычисляемое поле).
    """
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'header', 'text', 'category', 'created_at', 'comments_count', 'likes_count')
        read_only_fields = ('id', 'user', 'created_at', 'comments_count', 'likes_count')

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального представления модели Post.

    Поля:
    - id: id поста.
    - user: Пользователь, создавший пост.
    - header: Заголовок поста.
    - text: Текст поста.
    - created_at: Дата и время создания поста.
    - comments: Список комментариев к посту (вложенный сериализатор CommentSerializer).
    - comments_count: Количество комментариев под постом (вычисляемое поле).
    - likes_count: Количество лайков под постом (вычисляемое поле).
    """
    comments = CommentSerializer(many=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'category', 'header', 'text', 'created_at', 'comments_count', 'likes_count', 'comments')
        read_only_fields = ('id', 'user', 'created_at', 'comments_count', 'likes_count')

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'user', 'post', 'comment', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'created_at')


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'user', 'post', 'comment', 'text', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'created_at', 'text')
