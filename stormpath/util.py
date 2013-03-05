__author__ = 'ecrisostomo'

def assert_not_none(p_object, message):
    if p_object is None:
        raise ValueError(message)

def assert_instance(p_object, class_or_type_or_tuple, parameter_name):
    if not isinstance(p_object, class_or_type_or_tuple):
        full_name = class_or_type_or_tuple.__module__ + "." + class_or_type_or_tuple.__name__
        raise TypeError("{} must be an instance of {}.".format(parameter_name, full_name))

def assert_subclass(C, B, parameter_name):
    if not issubclass(C, B):
        full_name = B.__module__ + "." + B.__name__
        raise TypeError("{} must be a subclass of {}.".format(parameter_name, full_name))

def assert_true(statement, message):
    if (not statement):
        raise ValueError(message)
