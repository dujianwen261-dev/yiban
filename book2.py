from flask import Blueprint

bookbp2 = Blueprint('book2', __name__)

@bookbp2.route('/')
def index():
    return 'book2'

@bookbp2.route('/book2study')
def book2study():
    return 'book2study'
