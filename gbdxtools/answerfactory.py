"""
Classes to represent AnswerFactory Recipes, Projects.

Contact: nricklin@digitalglobe.com
Contact: mtrotter@digitalglobe.com
"""

class Recipe(object):
    def __init__(self, **kwargs):
        '''
        Construct an instance of an AnswerFactory Recipe

        Args:
            **kwargs

        Returns:
            An instance of a Recipe.

        '''


class Project(object):
    def __init__(self, **kwargs):
        '''
        Construct an instance of an AnswerFactory Project

        Args:
            **kwargs

        Returns:
            An instance of a Project.

        '''

        # Initialize by id
        if kwargs.get('id'):
        	pass
