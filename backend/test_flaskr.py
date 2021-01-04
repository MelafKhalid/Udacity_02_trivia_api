import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres','123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'when was the kingdom established?',
            'answer': 'september 23, 1932',
            'difficulty': 4,
            'category': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

# Test for each test for successful operation and for expected errors.

    def test_retrieve_categories(self):
        res =  self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['categories'])

    def test_retrieve_categories_failed(self):
        res =  self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])
        self.assertIsNotNone(data['categories'])

    def test_retrieve_questions_failed(self):
        res = self.client().get('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_questions(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_delete_questions_failed(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):

        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question_failed(self):
        
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['total_questions'])
        self.assertIsNotNone(len(data['questions']), 4)
        self.assertIsNotNone(data['current_category'])

    def test_search_question_failed(self):
        res = self.client().post('/questions/search', json={'searchTerm': "pineapplejuice"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        self.assertEqual(data['total_questions'], 0)
        self.assertFalse(len(data['questions']), 0)
        self.assertIsNotNone(data['current_category'], 0)



    def test_retrive_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'Science')

    def test_retrive_category_questions_failed(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    
    def test_play_quiz(self):


        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "5", "type": "History"
            }
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])


    def test_play_quiz_failed(self):

        res = self.client().post('/quizzes', json={
            "previous_questions": [], 
            "quiz_category": {
                "id": "6", "type": "Science"
            }
        })

        data = json.loads(res.data)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()