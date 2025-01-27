from rest_framework import serializers
from .models import Post, Comment, Like, PostImage
from users.serializers import UserSerializer, PartialUserSerializer


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'post', 'image']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    user = PartialUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'comments_count', 'likes_count', 'images', 'user']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SinglePostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'comments', 'likes', 'images']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def get_likes(self, obj):
        likes = obj.likes.all()
        return LikeSerializer(likes, many=True).data
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LikeSerializer(serializers.ModelSerializer):
    user_data = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'user_data']
        read_only_fields = ['id']

