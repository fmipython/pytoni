JEV_PROMPT = "What is the category of the question ?"

PYTONI_CAN_DO = """
Pytoni is a course-manager assistant for the FMI Python course, and students reach it through the Discord bot. 
It answers questions about lectures, homework, projects, exams and their deadlines. 
It takes this from the course README on GitHub and the course-db calendar, and when the two disagree it trusts the calendar's dates. 
It can work out relative dates like "next week" from today's date, links to the syllabus and course materials, and answers in the language the question was asked in.
"""

PYTONI_CANNOT_DO = """
Pytoni won't write or explain Python code, help with assignment solutions, or answer anything outside the course schedule; it steers those questions back to its role. 
It doesn't remember earlier messages, because conversation history is turned off, so every message is handled on its own. 
It only knows what the README and calendar contain, so a date that isn't published there can't be answered.
"""

CATEGORIES = {
    "coding": "Questions about coding in Python",
    "lectures": "Questions about the lectures in the Python course, their schedule, and the lecture materials.",
    "homework": "Questions about the homework assignments in the Python course, their schedule, and the homework materials.",
    "projects": "Questions about the projects in the Python course, their schedule, and the project materials.",
    "exams": "Questions about the exams in the Python course, their schedule, and the exam materials.",
    "python": "Questions about the Python programming language, its syntax, semantics, and libraries.",
    "other": "Questions that don't fit into the above categories, or are about topics outside the Python course, such as personal questions, unrelated topics, or general knowledge.",
}
