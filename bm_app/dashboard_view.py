from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


@login_required
def dashboard(request):
    return render(request, 'bm_app/dashboard.html', {})
