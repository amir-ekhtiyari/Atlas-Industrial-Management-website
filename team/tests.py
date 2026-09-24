from django.test import TestCase
from django.urls import reverse

from core.tests import make_company

from .models import TeamMember


def make_member(**overrides):
    data = {
        'full_name': 'عضو نمونه',
        'position': 'مهندس',
        'photo': 'team/sample.png',
    }
    data.update(overrides)
    for field in ('full_name', 'position'):
        value = data[field]
        data.setdefault(f'{field}_fa', value)
        data.setdefault(f'{field}_en', value)
    return TeamMember.objects.create(**data)


class TeamMemberModelTests(TestCase):
    def test_ordering_follows_order_field(self):
        make_member(full_name='دوم', order=20)
        make_member(full_name='اول', order=10)
        self.assertEqual([m.full_name for m in TeamMember.objects.all()], ['اول', 'دوم'])

    def test_str_returns_full_name(self):
        self.assertEqual(str(make_member(full_name='علی رضایی')), 'علی رضایی')


class TeamViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_company()
        make_member(full_name='عضو فعال', order=10)
        make_member(full_name='عضو غیرفعال', order=20, is_active=False)

    def test_list_shows_only_active_members(self):
        response = self.client.get(reverse('team:list'))
        self.assertEqual(response.status_code, 200)
        names = [m.full_name for m in response.context['members']]
        self.assertEqual(names, ['عضو فعال'])

    def test_template_used(self):
        response = self.client.get(reverse('team:list'))
        self.assertTemplateUsed(response, 'team/team_list.html')
