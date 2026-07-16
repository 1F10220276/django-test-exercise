from django.test import TestCase, Client
from django.utils import timezone
from datetime import datetime, timedelta
from todo.models import Category, Task



# Create your tests here.
class SampleTestCase(TestCase):
    def test_sample1(self):
        self.assertEqual(1 + 2, 3)


class TaskModelTestCase(TestCase):
    def test_create_task1(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        task = Task(title="task1", due_at=due)
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, "task1")
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, due)

    def test_create_task2(self):
        task = Task(title="task2")
        task.save()

        task = Task.objects.get(pk=task.pk)
        self.assertEqual(task.title, "task2")
        self.assertFalse(task.completed)
        self.assertEqual(task.due_at, None)

    def test_is_overdue_future(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))

    def test_is_overdue_past(self):
        due = timezone.make_aware(datetime(2024, 6, 30, 23, 59, 59))
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertTrue(task.is_overdue(current))

    def test_is_overdue_none(self):
        due = None
        current = timezone.make_aware(datetime(2024, 7, 1, 0, 0, 0))
        task = Task(title="task1", due_at=due)
        task.save()

        self.assertFalse(task.is_overdue(current))

    def test_is_due_soon_true(self):
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title="task1", due_at=current + timedelta(hours=3))
        task.save()

        self.assertTrue(task.is_due_soon(current))

    def test_is_due_soon_false(self):
        current = timezone.make_aware(datetime(2024, 6, 30, 0, 0, 0))
        task = Task(title="task1", due_at=current + timedelta(days=2))
        task.save()

        self.assertFalse(task.is_due_soon(current))


class TodoViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat1 = Category.objects.create(name="Work")
        self.cat2 = Category.objects.create(name="Personal")

    def test_index_get(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "todo/index.html")
        self.assertEqual(len(response.context["tasks"]), 0)

    def test_index_post(self):
        data = {"title": "Test Task", "due_at": "2024-06-30 23:59:59", "category": str(self.cat1.pk)}
        response = self.client.post("/", data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "todo/index.html")
        self.assertEqual(len(response.context["tasks"]), 1)

        task = Task.objects.get(title="Test Task")
        self.assertEqual(task.category, self.cat1)

    def test_index_get_search(self):
        Task.objects.create(title="Buy milk")
        Task.objects.create(title="Read book")
        response = self.client.get("/?search=buy")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0].title, "Buy milk")

    def test_index_get_category_filter(self):
        task1 = Task.objects.create(title="Work task", category=self.cat1)
        Task.objects.create(title="Personal task", category=self.cat2)
        response = self.client.get("/?category={}".format(self.cat1.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0], task1)

    def test_index_get_order_post(self):
        task1 = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title="task2", due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get("/?order=post")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "todo/index.html")
        self.assertEqual(response.context["tasks"][0], task2)
        self.assertEqual(response.context["tasks"][1], task1)

    def test_index_get_order_due(self):
        task1 = Task(title="task1", due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task1.save()
        task2 = Task(title="task2", due_at=timezone.make_aware(datetime(2024, 8, 1)))
        task2.save()
        client = Client()
        response = client.get("/?order=due")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "todo/index.html")
        self.assertEqual(response.context["tasks"][0], task1)
        self.assertEqual(response.context["tasks"][1], task2)

    def test_detail_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/detail.html')
        self.assertEqual(response.context['task'], task)

    def test_detail_get_fail(self):
        client = Client()
        response = client.get('/1/')

        self.assertEqual(response.status_code, 404)

    def test_delete_success(self):
        task = Task(title='task1')
        task.save()
        client = Client()
        response = client.get('/{}/delete'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_fail(self):
        client = Client()
        response = client.get('/999/delete')

        self.assertEqual(response.status_code, 404)
    def test_update_get_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)))
        task.save()
        client = Client()
        response = client.get('/{}/update'.format(task.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'todo/edit.html')
        self.assertEqual(response.context['task'], task)

    def test_update_post_success(self):
        task = Task(title='task1', due_at=timezone.make_aware(datetime(2024, 7, 1)), category=self.cat1)
        task.save()
        response = self.client.post(
            '/{}/update'.format(task.pk),
            {'title': 'updated task', 'due_at': '2024-07-02 12:00:00', 'category': str(self.cat2.pk)}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/{}/'.format(task.pk))

        updated_task = Task.objects.get(pk=task.pk)
        self.assertEqual(updated_task.title, 'updated task')
        self.assertEqual(updated_task.category, self.cat2)
        self.assertEqual(updated_task.due_at, timezone.make_aware(datetime(2024, 7, 2, 12, 0, 0)))

    def test_close_success(self):
        task = Task(title='task1', completed=False)
        task.save()
        response = self.client.get('/{}/close'.format(task.pk))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        finished_task = Task.objects.get(pk=task.pk)
        self.assertTrue(finished_task.completed)

    def test_close_fail(self):
        response = self.client.get('/999/close')

        self.assertEqual(response.status_code, 404)

    def test_index_get_category_invalid(self):
        Task.objects.create(title="Task A", category=self.cat1)
        Task.objects.create(title="Task B", category=self.cat2)
        response = self.client.get("/?category=abc")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 2)

    def test_index_get_search_and_category(self):
        Task.objects.create(title="Buy milk", category=self.cat1)
        Task.objects.create(title="Buy eggs", category=self.cat2)
        response = self.client.get("/?search=buy&category={}".format(self.cat1.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["tasks"]), 1)
        self.assertEqual(response.context["tasks"][0].title, "Buy milk")

    def test_index_context_preserves_search_and_category(self):
        Task.objects.create(title="Buy milk", category=self.cat1)
        response = self.client.get("/?search=buy&category={}".format(self.cat1.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search"], "buy")
        self.assertEqual(response.context["selected_category"], str(self.cat1.pk))
