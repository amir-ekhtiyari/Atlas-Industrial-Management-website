from django.shortcuts import render

from .models import TeamMember


def team_list(request):
    context = {
        'members': TeamMember.objects.filter(is_active=True),
    }
    return render(request, 'team/team_list.html', context)
