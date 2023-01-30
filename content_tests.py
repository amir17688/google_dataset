from nose.tools import *
from random import randrange
from copy import deepcopy
from flashcardstudy.content import ContentObject

test_contents = [[1, 'first', [[1, '1', '2'], [2, '3', '4'], [3, '5', '6']]], [2, 'second', [[1, 'foo', 'bar'], [2, 'red', 'blue'], [3, 'something', 'else']]]]

def create_test_content_obj():
	testobj = ContentObject(test_contents,'random','reverse')
	assert_is_instance(testobj, ContentObject)
	assert_equal(testobj.mode,('random','reverse'))
	assert_not_equal(testobj.mode,('random','reverse','randomstack'))
	assert_equal(testobj.contents, test_contents)

def test_fetching():
	testobj = ContentObject(test_contents,'')
	assert_equal(testobj.fetch(),'1')
	assert_equal(testobj.fetch(),'2')
	testobj.fetch()
	assert_equal(testobj.fetch(),'4')

def test_specific_fetching():
	original = deepcopy(test_contents)
	testobj = ContentObject(test_contents,'')
	sel_stack_id = 1
	sel_card_id = 2
	testobj.stack_id = sel_stack_id
	testobj.card_id = sel_card_id
	assert_equal(testobj.fetch(),original[sel_stack_id][2][sel_card_id][1])

def test_random_fetching_and_reverse():
	original = deepcopy(test_contents)
	testobj = ContentObject(test_contents,'random','reverse')
	sel_stack_id = randrange(0,len(original))
	sel_card_id = randrange(0,len(original[sel_stack_id][2])) 
	testobj.stack_id = sel_stack_id
	testobj.card_id = sel_card_id
	assert_equal(testobj.fetch(),original[sel_stack_id][2][sel_card_id][2])
