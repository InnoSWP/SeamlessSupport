import unittest
import requests
import Backend.firebase as firebase


class TestServerAPI(unittest.TestCase):
    email = 'random_email@email.com'
    server = 'http://127.0.0.1:5000/'
    question_id = 1
    message_id = 1
    volunteer_id = 1
    question_text = 'some text'

    def test_new_user(self):
        json = {
            'email': self.email
        }
        res = requests.post(self.server + 'api/v1/users', json=json).json()
        self.assertEqual(res, {})

        res = requests.get(self.server + 'api/v1/users', json=json).json()
        self.assertEqual(res.get('email'), json.get('email'))

    def test_site_working(self):
        res = requests.get(self.server)
        self.assertEqual(res.status_code, 200)

    def test_volunteer_declined(self):
        firebase.add_question(self.question_text, self.question_id, self.email)
        firebase.volunteer_accepted(self.question_id, self.message_id, self.volunteer_id)
        firebase.volunteer_declined(self.volunteer_id)

    def test_volunteer_answered(self):
        firebase.add_question(self.question_text, self.question_id, self.email)
        firebase.volunteer_accepted(self.question_id, self.message_id, self.volunteer_id)
        firebase.volunteer_answered(self.volunteer_id, 'answer')


if __name__ == '__main__':
    unittest.main()
