from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from todo.models import Category, Task


# Create your views here.
def index(request):
    categories = Category.objects.order_by("name")

    if request.method == "POST":
        category = None
        category_id = request.POST.get("category", "").strip()
        if category_id:
            try:
                category = Category.objects.get(pk=int(category_id))
            except (Category.DoesNotExist, ValueError):
                category = None

        due_at = None
        due_at_str = request.POST.get("due_at", "").strip()
        if due_at_str:
            due_at = make_aware(parse_datetime(due_at_str))

        priority = request.POST.get("priority", Task.PRIORITY_MEDIUM)

        task = Task(
            title=request.POST["title"],
            due_at=due_at,
            category=category,
            priority=priority,
        )
        task.save()

    tasks = Task.objects.all()
    search = request.GET.get("search", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if search:
        tasks = tasks.filter(title__icontains=search)

    if selected_category:
        try:
            tasks = tasks.filter(category_id=int(selected_category))
        except ValueError:
            pass

    if request.GET.get("order") == "due":
        tasks = tasks.order_by("due_at")
    else:
        tasks = tasks.order_by("-posted_at")

    context = {
        "tasks": tasks,
        "categories": categories,
        "selected_category": selected_category,
        "search": search,
    }
    return render(request, "todo/index.html", context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        "task": task,
    }

    return render(request, "todo/detail.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    categories = Category.objects.order_by("name")
    if request.method == "POST":
        category = None
        category_id = request.POST.get("category", "").strip()
        if category_id:
            try:
                category = Category.objects.get(pk=int(category_id))
            except (Category.DoesNotExist, ValueError):
                category = None

        due_at = None
        due_at_str = request.POST.get("due_at", "").strip()
        if due_at_str:
            due_at = make_aware(parse_datetime(due_at_str))

        task.title = request.POST["title"]
        task.due_at = due_at
        task.category = category
        task.priority = request.POST.get("priority", Task.PRIORITY_MEDIUM)
        task.save()
        return redirect("detail", task_id=task_id)

    context = {
        "task": task,
        "categories": categories,
    }
    return render(request, "todo/edit.html", context)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)
