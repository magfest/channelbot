import functools
import json
import os

initialcwd = os.getcwd()

data = None
perms = None
blacklist = None

def get_data():
    global data
    if data is None:
        with open("channelbot_data.json") as f:
            data = json.load(f)

    return data

def save_data(new_data=None):
    global data
    if new_data:
        data = new_data

    with open("channelbot_data.json", "w") as f:
        json.dump(data, f)

def get_perms():
    global perms
    if perms is None:
        with open("channelbot_perms.json") as f:
            perms = json.load(f)

    return perms

def get_blacklist():
    global blacklist
    if blacklist is None:
        try:
            with open("channelbot_blacklist.json") as f:
                blacklist = json.load(f)
        except:
            blacklist = []
            save_blacklist(blacklist)
    return blacklist

def save_blacklist(new_blacklist=None):
    global blacklist
    if new_blacklist:
        blacklist = new_blacklist
    
    with open("channelbot_blacklist.json", "w") as f:
        json.dump(blacklist, f)

def add_blacklist(entry):
    blacklist = get_blacklist()
    if not entry in blacklist:
        blacklist.append(entry)
    save_blacklist(blacklist)

def remove_blacklist(entry):
    blacklist = get_blacklist()
    if entry in blacklist:
        blacklist.remove(entry)
    save_blacklist(blacklist)

def test_blacklist(entry):
    return entry in get_blacklist()

def save_perms(new_perms=None):
    global perms
    if new_perms:
        perms = new_perms

    with open("channelbot_perms.json", "w") as f:
        json.dump(perms, f)

def _matched_perms(perm):
    parts = perm.split('.')

    for i in range(1, len(parts) + 1):
        yield '.'.join(parts[:i])
        yield '.'.join(parts[:i-1] + ['*'])

def grant_perm(user_id, permission):
    perms = get_perms()

    if user_id not in perms:
        perms[user_id] = []

    if permission not in perms[user_id]:
        perms[user_id].append(permission)

        save_perms(perms)

def revoke_perm(user_id, permission):
    perms = get_perms()

    if user_id not in perms:
        perms[user_id] = []

    if permission in perms[user_id]:
        del perms[user_id][perms[user_id].index(permission)]
        save_perms(perms)
        return True

    return False

def get_user_perms(user_id):
    return get_perms().get(user_id, [])

def has_perm_msg(message, *reqd_perms):
    return has_perm(message._get_user_id(), *reqd_perms)

def has_perm(user_id, *reqd_perms):
    user_perms = get_user_perms(user_id)
    for reqd_perm in reqd_perms:
        for ok_perm in _matched_perms(reqd_perm):
            if ok_perm in user_perms:
                break
        else:
            return False
    return True

def require_perm(*reqd_perms, msg="I'm sorry, I'm afraid I can't do that..."):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(message, *args):
            if has_perm(message._get_user_id(), *reqd_perms):
                return func(message, *args)
            else:
                message.reply(msg)

        setattr(wrapper, "permissions", reqd_perms)
        return wrapper

    return decorator
