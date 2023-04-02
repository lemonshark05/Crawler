import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure

# Define the MongoDB connection string
connection_string = "mongodb+srv://zmeng8:b2UtDhRV7BbttH6O@cluster0.ihvhz86.mongodb.net/?retryWrites=true&w=majority"

# Create a MongoDB client instance
client = MongoClient(connection_string)

db = client["leetcode"]

class LeetCode:
    def __init__(self, questionid, link, title, difficulty, description):
        self.questionid = questionid
        self.link = link
        self.title = title
        self.difficulty = difficulty
        self.description = description

def main():
    db.create_collection("problem")
    url = "https://leetcode.com/api/problems/all/"

    response = requests.get(url)
    data = response.json()
    questions = data['stat_status_pairs']

    for question in questions:
        questionid = question['stat']['frontend_question_id']
        link = "https://leetcode.com/problems/" + question['stat']['question__title_slug']
        title = question['stat']['question__title']
        difficulty = question['difficulty']['level']
        print('Question Number:', questionid)
        print('Link:', link)
        print('Title:', title)
        print('Difficulty:', difficulty)
        print('Submission Rate:', question['stat']['total_acs'] / question['stat']['total_submitted'])

        url1 = "https://leetcode.com/problems/" + question['stat']['question__title_slug']
        response = requests.get(url1)

        # Use BeautifulSoup to parse the HTML content of the response
        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            description = soup.currentTag.text.strip()
            leetcode = LeetCode(
                questionid=questionid,
                link=link,
                title=title,
                difficulty=difficulty,
                description=description
            )
            db.problem.insert_one(leetcode.__dict__)
        except AttributeError:
            description = 'It is locked !!!'
        print('Description: ', description)
        print('______________________________________________________________________________________________')

if __name__ == '__main__':
    main()