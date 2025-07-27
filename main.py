from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import os
from datetime import datetime

#Creating the app
app = FastAPI(title = "GroupLinker", description = "AI-powered group scheduling")

#This is how user data availability should look like to be compatible
class UserAvailability(BaseModel):
    name: str
    available_days: List[str]
    available_times: List[str]
    email: str = None

class GroupInfo(BaseModel):
    group_name: str
    description: str = ""
    created_by: str = ""

#Here all groups and their students are stored
# Format: {"group_name": {"info": {...}, "users": [...]}}
groups_data = {}

#this is a file to save data (simple persistance)
DATA_FILE = "groups_data.json"

def load_data():
    global groups_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                groups_data = json.load(f)
                print(f"Loaded {len(groups_data)} existing groups")
        except:
            groups_data = {}
            print("Started with empty data")
    else:
        groups_data = {}
        print("No existing data found, starting fresh")
    
def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(groups_data, f, ident = 2)
        return True
    
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

load_data()

@app.get("/")
def read_root():
    return {
        "message": "GroupLinker - AI-Powered Scheduler",
        "total_groups": len(groups_data),
        "groups": list(groups_data.keys())
    }

@app.post("/create_group")
def create_group(group: GroupInfo):
    if group.group_name in groups_data:
        raise HTTPException(status_code = 400, detail = "Group already exists!")

    groups_data[group.group_name] = {
        "info": {
            "description": group.description,
            "created_by": group.created_by,
            "created_at": datetime.now().isoformat()
        },
        "users": []
    }

    save_data()

    return {
        "message": f"Created group '{group.group_name}' successfully!",
        "group_url": f"/group/{group.group_name}"
    }


@app.get("/group/{group_name}")
def get_group_into(group_name: str):
    
    if group_name not in groups_data:
        raise HTTPException(status_code = 404, detail = "Group not found!")
    
    group_data = groups_data[group_name]
    return {
        "group_name": group_name,
        "info": group_data["info"],
        "users": group_data["users"],
        "user_count": len(group_data["users"]),
        "suggestion": get_group_suggestion(group_name)

    }

@app.post("/group/{group_name}/add_user")
def add_user_to_group(group_name: str, user: UserAvailability):
    if group_name not in groups_data:
        raise HTTPException(status_code = 404, detail = "Group not found!")
    
    existing_users = groups_data[group_name]["users"]
    for existing_user in existing_users:
        if existing_user["name"].lower() == user.name.lower():
            existing_users.remove(existing_user)
            break
    
    groups_data[group_name]["users"].append(user.dict())
    save_data()

    return{ 
        "message": f"Added {user.name} to group '{group_name}'",
        "total_users": len(groups_data[group_name]["users"])
    }

@app.get("/group/{group_name}/suggest")
def get_group_suggestion(group_name: str):
    if group_name not in groups_data:
        raise HTTPException(status_code = 404, detail = "Group not found!")
    
    users = groups_data[group_name]["users"]

    if len(users) < 2:
        return {
            "message": f"Need at least 2 people in '{group_name}' to suggest times",
            "user_count": len(users)
        }
    
    common_days = find_common_days(users)
    common_times = find_common_times(users)

    if common_days and common_times:
        suggestion = f"Everyone in '{group_name}' can meet on {common_days[0]} at {common_times[0]}."
    else:
        suggestion = f"No times work for everyone in '{group_name}'. Consider splitting into smaller groups."
    
    return {
        "group_name": group_name,
        "common_days": common_days,
        "common_times": common_times,
        "suggestion": suggestion,
        "user_count": len(users)
    }

#delete a group
@app.delete("/group/{group_name}")
def delete_group(group_name: str):
    if group_name not in groups_data:
        raise HTTPException(status_code=404, detail="Group not found!")
    
    del groups_data[group_name]
    save_data()  
    return {"message": f"Deleted group '{group_name}'"}

@app.get("/groups")
def list_all_groups():
    group_summary = []

    for group_name, data in groups_data.items():

        group_summary_append({
            "name": group_name,
            "description": data["info"]["description"],
            "user_count": len(data["users"]),
            "created_at": data["info"]["created_at"]
        })

    return {
        "groups": group_summary,
        "total_groups": len(groups_data)
    }

def find_common_days(users_list):
    if not users_list:
        return []
    
    common = set(users_list[0]["available_days"])

    for user in users_list[1:]:
        user_days = set(user["available_days"])
        common = common.intersection(user_days)
    
    return list(common)

def find_common_times(users_list):
    if not users_list:
        return []
    
    common = set(users_list[0]["available_times"])

    for user in users_list[1:]:
        user_times = set(user["available_times"])
        common = common.intersection(user_times)
    
    return list(common)