from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure
from faker import Faker
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import random

userlist = []
goallist = []
todolist = []
tasklist = []
# fake leetcode data
leettodo = []
leetgoals = ["Complete the Google company LeetCode question bank",    "Complete the Apple company LeetCode question bank",    "Complete the Microsoft company LeetCode question bank",    "Complete the Facebook company LeetCode question bank",    "Complete the Amazon company LeetCode question bank",    "Complete the top 20 LeetCode questions",    "Complete the top 100 LeetCode questions",    "Complete the LeetCode questions about sorting algorithms",    "Complete the LeetCode questions about dynamic programming",    "Complete the LeetCode questions about binary trees",    "Complete the LeetCode questions about graphs",    "Complete the LeetCode questions about arrays and strings",    "Complete the LeetCode questions about recursion",    "Complete the LeetCode questions about backtracking",    "Complete the LeetCode questions about sliding windows",    "Complete the LeetCode questions about greedy algorithms",    "Complete the LeetCode questions about two pointers",    "Complete the LeetCode questions about linked lists",    "Complete the LeetCode questions about stacks and queues",    "Complete the LeetCode questions about bit manipulation",    "Complete the LeetCode questions about math",    "Complete the LeetCode questions about searching and sorting",    "Complete the LeetCode questions about design problems",    "Complete the LeetCode questions about database systems",    "Complete the LeetCode questions about system design"]
leetlist = []
# Define the MongoDB connection string
connection_string = "mongodb+srv://zmeng8:b2UtDhRV7BbttH6O@cluster0.ihvhz86.mongodb.net/?retryWrites=true&w=majority"

# Create a MongoDB client instance
client = MongoClient(connection_string)

# Connect to the "learn" database
db = client["learn"]
leet_db = client["leetcode"]
# goallist = [GoalItem(ObjectId(), fake.date_this_month(), 3)]

class GoalItem:
    def __init__(self, goalid, dueDate, timePreDay):
        self.goalid = goalid
        self.dueDate = dueDate
        self.timePreDay = timePreDay

class User:
    def __init__(self, password, username, title, email, todolist=None, goallist=None, tasklist=None):
        self.username = username
        self.password = password
        self.title = title
        self.email = email
        self.todolist = todolist or []
        self.goallist = goallist or []
        self.tasklist = tasklist or []

class Goal:
    def __init__(self, title, description, createdDate, recommendTerms, author, category, todolist=None, sharedWith=None):
        self.title = title
        self.description = description
        self.createdDate = createdDate
        self.recommendTerms = recommendTerms
        self.author = author
        self.category = category
        self.todolist = todolist or []
        self.sharedWith = sharedWith or []

class Todo:
    def __init__(self, title, goalid, description, createdDate, expectedTimeTake, difficultyLevel, tasklist=None, sharedWith=None):
        self.title = title
        self.goalid = goalid
        self.description = description
        self.createdDate = createdDate
        self.expectedTimeTake = expectedTimeTake
        self.difficultyLevel = difficultyLevel
        self.tasklist = tasklist or []
        self.sharedWith = sharedWith or []

class Performance:
    def __init__(self, learningZone, completed, actualTimeTake):
        self.learningZone = learningZone
        self.completed = completed
        self.actualTimeTake = actualTimeTake

class Task:
    def __init__(self, reviewDate, dueDate, active, performance=None, todoId=None, userId=None, goalId=None):
        self.reviewDate = reviewDate
        self.dueDate = dueDate or ""
        self.todoId = todoId or ""
        self.userId = userId or ""
        self.goalId = goalId or ""
        self.performance = performance or []
        self.active = active or False

def create_user_collection():
    # Create a "users" collection for the User class
    try:
        db.create_collection("users")
    except OperationFailure:
        pass
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)

def record_user_collection():

    for user in db["users"].find():
        userlist.append(user["_id"])

def create_goal_collection():
    # Create a "goals" collection for the Goal class
    try:
        db.create_collection("goals")
    except OperationFailure:
        pass

    fake = Faker()
    for goalname in leetgoals:
        author_id = random.choice(userlist)
        shared_with = []
        shared_number = random.randint(2, 5)
        while len(shared_with) < shared_number:
            user_id = random.choice(userlist)
            if user_id != author_id and user_id not in shared_with:
                shared_with.append(user_id)
        goal = Goal(
            title=goalname,
            description=goalname,
            createdDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            recommendTerms = random.randint(7,30),
            author=author_id,
            category=fake.random_element(elements=("learn", "Career", "leetcode")),
            # todolist=random.sample(todolist, random.randint(1, 5)),
            sharedWith=shared_with
        )
        db.goals.insert_one(goal.__dict__)
        goallist.append((goal._id, goal.author, goal.sharedWith))
        goal_item = GoalItem(goalid=goal._id, dueDate=(datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S"), timePreDay=random.randint(7,30))
        db.users.update_one({"_id": author_id}, {"$push": {"goallist": goal_item.__dict__}})
        for userid in shared_with:
            db.users.update_one({"_id": userid}, {"$push": {"goallist": goal_item.__dict__}})


def create_todo_collection():
    # Create a "todolist" collection for the Todo class
    try:
        db.create_collection("todolist")
    except OperationFailure:
        pass

    fake = Faker()
    for goal_id, author, shared_with  in goallist:
        goalId = goal_id
        sharedlist = shared_with
        sharedlist.append(author)
        for i in range(random.randint(2, 5)):
            todo = Todo(
                title=fake.sentence(),
                description=fake.paragraph(),
                createdDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                expectedTimeTake=random.randint(10, 30),
                difficultyLevel=random.randint(1, 3),
                #tasklist=random.sample(userlist, 1),
                sharedWith=sharedlist,
                goalid=goalId
            )
            db.todolist.insert_one(todo.__dict__)
            todolist.append((todo._id, goalId, sharedlist))
            db.goals.update_one({"_id": goal_id}, {"$push": {"todolist": todo._id}})
            for userid in sharedlist:
                db.users.update_one({"_id": userid}, {"$push": {"todolist": todo._id}})


def create_task_collection():
    # Create the "tasks" collection
    try:
        db.create_collection("tasks")
    except:
        pass
    # Create some fake data
    fake = Faker()

    # Insert some tasks into the collection
    for todolist_id, goal_id, sharedlist in todolist:
        reviewDate = datetime.now() + timedelta(days=random.randint(20, 30))
        dueDate = datetime.now() + timedelta(days=random.randint(1, 20))
        for sharedId in sharedlist:
            performance = Performance(learningZone=random.randint(1, 3), completed=(datetime.now() + timedelta(days=random.randint(3, 10))).strftime("%Y-%m-%d %H:%M:%S"),
                                       actualTimeTake=random.randint(10, 60))
            task = Task(
                todoId=todolist_id,
                userId=sharedId,
                goalId=goal_id,
                reviewDate=reviewDate.strftime("%Y-%m-%d %H:%M:%S"),
                dueDate=dueDate.strftime("%Y-%m-%d %H:%M:%S"),
                #we add performance which contain learning zone/complete date/ actualtime take
                performance=[performance.__dict__],
                active=False
            )
            db.tasks.insert_one(task.__dict__)
            tasklist.append((task._id, goal_id, todolist_id, sharedId))
            db.todolist.update_one({"_id": todolist_id}, {"$push": {"tasklist": task._id}})
            db.users.update_one({"_id": sharedId}, {"$push": {"tasklist": task._id}})


def delete_all():
    db = client["learn"]

    db.drop_collection("goals")
    db.drop_collection("todolist")
    db.drop_collection("tasks")

if __name__ == '__main__':
    # delete_all()
    # db.drop_collection("users")
    # create_user_collection()
    record_user_collection()
    create_goal_collection()
    create_todo_collection()
    create_task_collection()