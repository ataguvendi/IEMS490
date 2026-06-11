import json
import os

TODO_FILE = "todos.json"


def load_todos():
    # Load todos from file
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        todos = json.load(f)
    return todos


def save_todos(todos):
    # Save todos to file
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f)


def add_todo(todos, text):
    todo = {
        "id": len(todos) + 1,
        "text": text,
        "done": False
    }
    todos.append(todo)
    save_todos(todos)
    print(f"Added: {text}")


def complete_todo(todos, todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            save_todos(todos)
            print(f"Completed: {todo['text']}")
            return
    print("Todo not found")


def delete_todo(todos, todo_id):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            removed = todos.pop(i)
            save_todos(todos)
            print(f"Deleted: {removed['text']}")
            return
    print("Todo not found")


def list_todos(todos):
    if len(todos) == 0:
        print("No todos!")
        return
    print("\nYour todos:")
    for todo in todos:
        status = "x" if todo["done"] else " "
        print(f"  [{status}] {todo['id']}. {todo['text']}")
    print()


def show_menu():
    print("1. List todos")
    print("2. Add todo")
    print("3. Complete todo")
    print("4. Delete todo")
    print("5. Quit")


def main():
    todos = load_todos()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_todos(todos)
        elif choice == "2":
            text = input("Enter todo: ").strip()
            if text == "":
                print("Todo can't be empty")
            else:
                add_todo(todos, text)
        elif choice == "3":
            list_todos(todos)
            try:
                todo_id = int(input("Enter todo ID to complete: "))
                complete_todo(todos, todo_id)
            except ValueError:
                print("Please enter a valid number")
        elif choice == "4":
            list_todos(todos)
            try:
                todo_id = int(input("Enter todo ID to delete: "))
                delete_todo(todos, todo_id)
            except ValueError:
                print("Please enter a valid number")
        elif choice == "5":
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()