# File management logic: create, edit, retrieve

def create_file(name, content):
    with open(f"files/{name}", "w") as f:
        f.write(content)
