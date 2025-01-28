from django.shortcuts import render
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, PostImageSerializer, SinglePostSerializer
from rest_framework import generics
from .models import Post, Comment, Like, PostImage
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import APIException
from users.permissions import IsAdmin
from users.models import User
from product.models import Product

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
            images = self.request.FILES.getlist('images')
            if images:
                post_images = [PostImage(post=serializer.instance, image=image) for image in images]
                PostImage.objects.bulk_create(post_images)
        except Exception as e:
            raise APIException(f"Error creating post: {e}")


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    ## allow unauthenticated users to view posts
    authentication_classes = []
    permission_classes = []
    queryset = Post.objects.filter(status='approved').prefetch_related('comments', 'likes', 'images')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    
    pagination_class = PageNumberPagination


class PostDetailView(generics.RetrieveAPIView):
    serializer_class = SinglePostSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    ## allow unauthenticated users to view posts
    authentication_classes = []
    permission_classes = []
    queryset = Post.objects.select_related().prefetch_related('comments', 'likes', 'images')


class PostUpdateView(generics.UpdateAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        try:
            serializer.save(user=self.request.user)
            images = self.request.FILES.getlist('images')
            if images:
                post_images = [PostImage(post=serializer.instance, image=image) for image in images]
                PostImage.objects.bulk_create(post_images)
        except Exception as e:
            raise APIException(f"Error updating post: {e}")


class PostDeleteView(generics.DestroyAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()

    def perform_destroy(self, instance):
        try:
            instance.images.all().delete()
            super().perform_destroy(instance)
        except Exception as e:
            raise APIException(f"Error deleting post: {e}")


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            post_id = self.request.data.get('post')
            if not Post.objects.filter(id=post_id).exists():
                raise NotFound('Post not found')
            serializer.save(user=self.request.user)
        except Exception as e:
            raise APIException(f"Error creating comment: {e}")


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            post_id = self.request.query_params.get('post')
            if not Post.objects.filter(id=post_id).exists():
                raise NotFound('Post not found')
            return Comment.objects.filter(post_id=post_id)
        except Exception as e:
            raise APIException(f"Error retrieving comments: {e}")


class CommentUpdateView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()


class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()


class LikeToggleView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(id=request.data['post'])
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        try:
            like = Like.objects.filter(user=request.user, post=post)
            if like.exists():
                like.delete()
                return Response({'message': 'Like removed'}, status=status.HTTP_200_OK)
            else:
                Like.objects.create(user=request.user, post=post)
                return Response({'message': 'Like added'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise APIException(f"Error toggling like: {e}")


class LikePostListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            post_id = self.kwargs.get('pk')
            if not Post.objects.filter(id=post_id).exists():
                raise NotFound('Post not found')
            return Like.objects.filter(post_id=post_id).select_related('user')
        except Exception as e:
            raise APIException(f"Error retrieving likes: {e}")

class ChangePostStatusView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(id=self.kwargs.get('pk'))
        except Post.DoesNotExist:
            raise NotFound('Post not found')

        try:
            post.status = request.data['status']
            post.save()
            data = PostSerializer(post).data
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            raise APIException(f"Error changing post status: {e}")
        
class PostListAdminView(generics.ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    queryset = Post.objects.prefetch_related('comments', 'likes', 'images')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = PageNumberPagination


# Create your views here.
class AdminCountView(APIView):
    def get(self, request):
        posts = Post.objects.count()
        pending_posts = Post.objects.filter(status='pending').count()
        approved_posts = Post.objects.filter(status='approved').count()
        rejected_posts = Post.objects.filter(status='rejected').count()

        products = Product.objects.count()

        users = User.objects.count()
        ##admin users
        admins = User.objects.filter(is_admin=True).count()
        ##normal users
        normal_users = User.objects.filter(is_admin=False).count()

        data = {
            'posts': posts,
            'pending_posts': pending_posts,
            'approved_posts': approved_posts,
            'rejected_posts': rejected_posts,
            'products': products,
            'users': users,
            'admins': admins,
            'normal_users': normal_users
        }

        return Response(data, status=status.HTTP_200_OK)
