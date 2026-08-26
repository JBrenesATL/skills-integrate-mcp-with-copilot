from copy import deepcopy
import unittest

from fastapi import HTTPException

import app


class SignupTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(app.activities)

    def tearDown(self):
        app.activities.clear()
        app.activities.update(self.original_activities)

    def test_valid_signup_normalizes_email(self):
        result = app.signup_for_activity(
            "Chess Club", " New.Student@Example.COM "
        )

        self.assertEqual(
            result,
            {"message": "Signed up new.student@example.com for Chess Club"},
        )
        self.assertIn(
            "new.student@example.com",
            app.activities["Chess Club"]["participants"],
        )

    def test_invalid_email_is_rejected(self):
        participants = app.activities["Chess Club"]["participants"]

        with self.assertRaisesRegex(HTTPException, "Invalid email address"):
            app.signup_for_activity("Chess Club", "not-an-email")

        self.assertEqual(participants, self.original_activities["Chess Club"]["participants"])

    def test_duplicate_signup_is_case_insensitive(self):
        participants = app.activities["Chess Club"]["participants"]

        with self.assertRaisesRegex(HTTPException, "already signed up"):
            app.signup_for_activity("Chess Club", " MICHAEL@MERGINGTON.EDU ")

        self.assertEqual(participants, self.original_activities["Chess Club"]["participants"])

    def test_full_activity_rejects_signup_without_mutation(self):
        activity = app.activities["Math Club"]
        activity["participants"] = [
            f"student{index}@example.com"
            for index in range(activity["max_participants"])
        ]
        participants_before_signup = list(activity["participants"])

        with self.assertRaisesRegex(HTTPException, "Activity is full"):
            app.signup_for_activity("Math Club", "extra@example.com")

        self.assertEqual(activity["participants"], participants_before_signup)


if __name__ == "__main__":
    unittest.main()