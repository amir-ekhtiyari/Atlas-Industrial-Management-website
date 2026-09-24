from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Post, PostCategory

PAGE_SIZE = 9


def post_list(request):
    posts = Post.objects.published().with_related()

    category_slug = request.GET.get('category') or ''
    active_category = None
    if category_slug:
        active_category = PostCategory.objects.filter(slug=category_slug).first()
        if active_category:
            posts = posts.filter(category=active_category)

    paginator = Paginator(posts, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': PostCategory.objects.filter(posts__is_published=True).distinct(),
        'active_category': active_category,
    }
    return render(request, 'news/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects.published().with_related(), slug=slug)
    related = (
        Post.objects.published()
        .with_related()
        .exclude(pk=post.pk)
    )
    if post.category_id:
        related = related.filter(category_id=post.category_id)

    context = {
        'post': post,
        'related_posts': related[:3],
    }
    return render(request, 'news/post_detail.html', context)
