from django.shortcuts import render, redirect

# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("reviews:index")

    else:
        form = CustomUserCreationForm()
    context = {"form": form}
    return render(request, "accounts/signup.html", context)


def detail(request, pk):
    user = get_user_model().objects.get(pk=pk)
    context = {"user": user}
    return render(request, "accounts/detail.html", context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get("next") or "reviews:index")
    else:
        form = AuthenticationForm()
    context = {"form": form}
    return render(request, "accounts/login.html", context)


def logout(request):
    auth_logout(request)
    messages.warning(request, "๋ก๊ทธ์์")
    return redirect("reviews:index")


@login_required
def update(request):
    form = CustomUserChangeForm(instance=request.user)
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:detail", request.user.pk)
    context = {"form": form}
    return render(request, "accounts/update.html", context)


def delete(request):
    if request.user.is_authenticated:
        request.user.delete()
        auth_logout(request)
        return redirect("accounts:login")


def update_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            ## ๋น๋ฐ๋ฒํธ ๋ณ๊ฒฝ ์, ๋ก๊ทธ์ธ ์?๋ณด๊ฐ ์ฌ๋ผ์ง ๊ทธ๋์ ๋น๋ฐ๋ฒํธ ๋ณ๊ฒฝ ํ๊ณ?๋ ๋ก๊ทธ์ธ ์?์ง๋ฅผ ์ํด์
            update_session_auth_hash(request, user)
            return redirect("accounts:detail", request.user.id)
    context = {"form": form}
    return render(request, "accounts/update_password.html", context)


def index(request):
    members = get_user_model().objects.all()
    return render(request, "accounts/index.html", {"members": members})


@login_required
def follow(request, user_pk):
    person = get_user_model().objects.get(pk=user_pk)
    if person != request.user:
        if person.followers.filter(pk=request.user.pk).exists():
            person.followers.remove(request.user)
        else:
            person.followers.add(request.user)
    return redirect("accounts:detail", user_pk)
