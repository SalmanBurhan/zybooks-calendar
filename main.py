from ics import Calendar, Event
from pprint import pprint
import requests


def send_post(url, payload, headers=None):
    if headers:
        r = requests.post(url, json=payload, headers=headers)
        return r.json()
    else:
        r = requests.post(url, json=payload)
        return r.json()


def send_get(url, params):
    r = requests.get(url, params=params)
    return r.json()


def build_ical(email: str, password: str):

    login_payload = {"email": email, "password": password}

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'connection': 'keep-alive',
        'content-type': 'application/json',
        'host': 'zyserver.zybooks.com',
        'origin': 'learn.zybooks.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }

    login_data = send_post("https://zyserver.zybooks.com/v1/signin", login_payload, headers=headers)

    if login_data['success']:
        print("Login Success")

        # print(login_data)
        calendar = Calendar()

        auth_token = login_data['session']['auth_token']
        user_id = login_data['user']['user_id']

        get_classes_url = 'https://zyserver.zybooks.com/v1/user/' + str(user_id) + '/items'
        get_classes_params = {'items': '["zybooks"]', 'auth_token': auth_token}

        get_classes_data = send_get(get_classes_url, get_classes_params)

        for subject in get_classes_data['items']['zybooks']:
            zybook_code = subject['zybook_code']
            if "CSUSM" not in zybook_code: continue;
            course_number = subject['course']['course_call_number']

            class_assignments_url = f'https://zyserver.zybooks.com/v1/zybook/{zybook_code}/assignments'
            class_assignments_params = {'auth_token': auth_token}

            class_assignments_data = send_get(class_assignments_url, class_assignments_params)

            print(f'## START {zybook_code} ##')
            for assignment in class_assignments_data['assignments']:
                assignment_name = assignment['title']
                due_date = assignment['due_dates'][0]['date']
                total_points: int = 0;
                sections: str = ''
                for section in assignment['sections']:
                    total_points += section['total_points']
                    sections += f"{section['chapter_number']}.{section['section_number']} - {section['title']}\n"
                #print(f'Assignment ==> {assignment_name}, Due Date ==> {due_date}\nTotal Points ==> {total_points}\nSections ==> \n{sections}')
                event = Event()
                event.name = f"{course_number} - {assignment_name}"
                event.begin = due_date
                event.description = f'Total Points: {total_points}\n Sections:\n----\n{sections}----'
                event.url = f'https://learn.zybooks.com/zybook/{zybook_code}?selectedPanel=assignments-panel'
                calendar.events.add(event)
            print(f'## END {zybook_code} ##')

            with open('ZyBooks.ics', 'w') as f:
                f.writelines(calendar.serialize_iter())

if __name__ == "__main__":
    build_ical(email=None, password=None)