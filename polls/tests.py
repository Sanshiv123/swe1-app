import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        old = Question(pub_date=timezone.now() - datetime.timedelta(days=30))
        self.assertIs(old.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        recent = Question(pub_date=timezone.now() - datetime.timedelta(hours=1))
        self.assertIs(recent.was_published_recently(), True)


class PollsViewTests(TestCase):
    def test_index_with_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_index_shows_question(self):
        Question.objects.create(question_text="Test question?", pub_date=timezone.now())
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "Test question?")

    def test_detail_view(self):
        q = Question.objects.create(question_text="Detail?", pub_date=timezone.now())
        response = self.client.get(reverse("polls:detail", args=(q.id,)))
        self.assertContains(response, "Detail?")

    def test_vote_without_choice_shows_error(self):
        q = Question.objects.create(question_text="Vote?", pub_date=timezone.now())
        response = self.client.post(reverse("polls:vote", args=(q.id,)))
        self.assertContains(response, "You didn&#x27;t select a choice.")

    def test_vote_redirects_to_results(self):
        q = Question.objects.create(question_text="Vote?", pub_date=timezone.now())
        c = q.choice_set.create(choice_text="Yes", votes=0)
        response = self.client.post(
            reverse("polls:vote", args=(q.id,)), {"choice": c.id}
        )
        self.assertRedirects(response, reverse("polls:results", args=(q.id,)))
        c.refresh_from_db()
        self.assertEqual(c.votes, 1)
