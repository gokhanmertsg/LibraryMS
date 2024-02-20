from enum import Enum

class BookStatusEnum(Enum):
    """
    Enumareter for the book status(integer).
    1: Borrowed
    2: Returned
    """
    BORROWED = 1
    RETURNED = 2

class BookTypeEnum(Enum):
    """
    Enumareter for the book type(integer).
    1: Reading
    2: School
    """
    READING = 2
    SCHOOL = 3