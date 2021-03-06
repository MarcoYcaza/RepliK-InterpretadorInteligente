from django.shortcuts import render, get_object_or_404
from django.db.models import Q # New
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, PostImage

def hackaton(request):
    return render(request,'blog/hackaton.html',{'key':'value'})

def home(request):
    posts=Post.objects.all()

    context = {
        'posts': posts
    }

    #print(posts)

    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 6


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

def PostDetailView(request, slug):
    post = get_object_or_404(Post, slug=slug)
    subcontent = PostImage.objects.filter(post=post)
    
    slug_url_kwarg = 'slug' #NEW

    indexed_subcontent = list(enumerate(subcontent))

    #print(indexed_subcontent)

    return render(request, 'blog/post_detail.html', {
        'object':post,
        'indexed_subcontent':indexed_subcontent
    })

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

class PostSearchListView(ListView):

    template_name = 'blog/search.html'
    #paginate_by = 6

    def get_queryset(self):
        
        filters = Q(title__icontains=self.query())

        # SELECT * FROM products WHERE title like %valor%

        #Post.objects.filter(filters)[:5]
        return Post.objects.filter(filters)

    def query(self):

        return self.request.GET.get('q')
    
    def get_context_data(self,**kwargs):

        context = super().get_context_data(**kwargs)

        context['query'] = self.query()

        context['count'] = context['post_list'].count()

        
        return context


