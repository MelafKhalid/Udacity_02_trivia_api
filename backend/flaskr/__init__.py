import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Return 10 questions per page.
QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):

  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end] 
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  

  # Set up CORS. Allow '*' for origins.

  CORS(app, resources={'/': {'origins': '*'}}) 

  # Use the after_request decorator to set Access-Control-Allow Headers and Access-Control-Allow Methods.

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

 # An endpoint to handle GET requests for all available categories.

  @app.route('/categories', methods=['GET'])
  def retrieve_categories():
    try:
      result = Category.query.order_by(Category.type).all()

      if len(result) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'categories': {category.id: category.type for category in result},
      })

    except:
      abort(404)

  # handle GET requests for all questions, including pagination (every 10 questions) and the endpoint will return a list of questions, number of total questions, current category, categories.. 
  
  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    try:
      total_questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, total_questions)
      total_category = Category.query.order_by(Category.type).all()
   
      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(total_questions),
        'categories': {category.id: category.type for category in total_category},
        'current_category':None
      })
    except:
      abort(404)

#  An endpoint to DELETE question When you click the trash icon using a question ID. 

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })

    except:
      abort(422)

# An endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.

  @app.route('/questions', methods=['POST'])
  def create_question():
      
    try:
      new_question = request.get_json().get('question', None)
      new_answer = request.get_json().get('answer', None)
      new_difficulty = request.get_json().get('difficulty', None)
      new_category = request.get_json().get('category', None)
      
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id,
      }) 

    except:
      abort(422)

# A POST endpoint to get questions based on a search term. 

  @app.route('/questions/search', methods=['POST'])
  def search_question():

    try:
      search_term = request.get_json().get('searchTerm')

      if search_term:
         result = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search_term}%')).all()

      return jsonify({
        'success': True,
        'questions': [question.format() for question in result],
        'total_questions': len(result),
        'current_category': None
      })

    except:
      abort(404)

# Create a GET endpoint to get questions based on category when clicking on one of the categories in the left column will cause only questions of that category to be shown. 

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def retrieve_category_questions(category_id):

    try:
      result = Question.query.order_by(Question.id).filter_by(category=category_id).all()

      if result:

        return jsonify({
          'success': True,
          'questions': [question.format() for question in result],
          'total_questions': len(result),
          'current_category': [question.category for question in result]
        })

    except:
      abort(404)

# A POST endpoint that take category and previous question parameters to get random questions within the given category to play the quiz.
  
  @app.route('/quizzes', methods=['POST'])
  def random_quiz():
    
    try:

      quiz_category = request.get_json().get('quiz_category')

      if quiz_category is None:
        abort(404)
      
      previous_questions = request.get_json().get('previous_questions')

      if quiz_category['id'] == 0:
        questions = Question.query.all()
      else:
        questions = Question.query.filter_by(category=quiz_category['id']).all()
      
      total_questions =  [question.format() for question in questions if question.id not in previous_questions]
     
      return jsonify({
        'success':True,
        'question': random.choice(total_questions)
      })

    except:
      abort(422)

 
# An error handlers for all expected errors.
 
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  return app
