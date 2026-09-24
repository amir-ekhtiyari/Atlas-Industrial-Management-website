from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.tests import make_company

from .models import Post, PostCategory


def make_post(**overrides):
    data = {
        'title': 'خبر نمونه',
        'summary': 'خلاصه خبر',
        'body': 'متن کامل خبر',
    }
    data.update(overrides)
    for field in ('title', 'summary', 'body'):
        value = data[field]
        data.setdefault(f'{field}_fa', value)
        data.setdefault(f'{field}_en', value)
    return Post.objects.create(**data)


class PostModelTests(TestCase):
    def test_slug_is_generated_from_title(self):
        post = make_post(title='گزارش تولید سال جدید')
        self.assertTrue(post.slug)
        self.assertEqual(post.get_absolute_url(),
                         reverse('news:detail', kwargs={'slug': post.slug}))

    def test_meta_description_falls_back_to_summary(self):
        post = make_post()
        self.assertEqual(post.display_meta_description, post.summary)
        post.meta_description = 'توضیح سئو'
        self.assertEqual(post.display_meta_description, 'توضیح سئو')

    def test_published_queryset_excludes_drafts_and_future_posts(self):
        make_post(slug='live')
        make_post(slug='draft', is_published=False)
        make_post(slug='scheduled', published_at=timezone.now() + timedelta(days=2))
        self.assertEqual([p.slug for p in Post.objects.published()], ['live'])

    def test_default_ordering_is_newest_first(self):
        make_post(slug='older', published_at=timezone.now() - timedelta(days=3))
        make_post(slug='newer', published_at=timezone.now() - timedelta(days=1))
        self.assertEqual([p.slug for p in Post.objects.all()], ['newer', 'older'])


class PostViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_company()
        cls.category = PostCategory.objects.create(name='رویدادها', slug='events')
        cls.other = PostCategory.objects.create(name='فنی', slug='technical')
        cls.post = make_post(slug='expo-2024', category=cls.category)
        make_post(slug='tech-note', category=cls.other)
        make_post(slug='draft-post', is_published=False)

    def test_list_shows_only_published_posts(self):
        response = self.client.get(reverse('news:list'))
        self.assertEqual(response.status_code, 200)
        slugs = [p.slug for p in response.context['posts']]
        self.assertNotIn('draft-post', slugs)
        self.assertEqual(len(slugs), 2)

    def test_category_filter_narrows_results(self):
        response = self.client.get(reverse('news:list'), {'category': 'events'})
        self.assertEqual(response.context['active_category'], self.category)
        self.assertEqual([p.slug for p in response.context['posts']], ['expo-2024'])

    def test_category_facets_exclude_categories_without_published_posts(self):
        PostCategory.objects.create(name='خالی', slug='empty')
        response = self.client.get(reverse('news:list'))
        self.assertNotIn('empty', {c.slug for c in response.context['categories']})

    def test_detail_page_renders(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/post_detail.html')

    def test_related_posts_share_category_and_exclude_self(self):
        sibling = make_post(slug='expo-recap', category=self.category)
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual([p.slug for p in response.context['related_posts']], [sibling.slug])

    def test_draft_detail_returns_404(self):
        draft = Post.objects.get(slug='draft-post')
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)
