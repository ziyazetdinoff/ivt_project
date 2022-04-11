import requests
from jinja2 import Template
import json
from datetime import date
from datetime import datetime
import plotly.express as px
import os


edu_email = os.environ['edu_email']
miem_email = os.environ['miem_email']
zulip_begin_date = "2022-01-01"
token = os.environ['token']
end_date = str(date.today())
zulip_response = requests.post("http://94.79.54.21:3000/api/zulip/getData",
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps({"studEmail": miem_email,
                                                "beginDate": zulip_begin_date,
                                                "endDate": end_date,
                                                "token": token,
                                                "timeRange": 1}))
jitsi_begin_date = "2021-09-15"
jitsi_rooms = []
jitsi_1response = requests.post("http://94.79.54.21:3000/api/jitsi/sessions",
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({"studEmail": miem_email,
                                                 "beginDate": jitsi_begin_date,
                                                 "endDate": end_date,
                                                 "token": token}))
jitsi_2response = requests.post("http://94.79.54.21:3000/api/jitsi/sessions",
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({"studEmail": edu_email,
                                                 "beginDate": jitsi_begin_date,
                                                 "endDate": end_date,
                                                 "token": token}))
git_begin_date = "2022-01-01"
git_response = requests.post("http://94.79.54.21:3000/api/git/getData",
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({"studEmail": edu_email,
                                              "beginDate": git_begin_date,
                                              "endDate": end_date,
                                              "timeRange": 1,
                                              "hideMerge": True,
                                              "token": token}),
                             timeout=5)
taiga_tasks_response = requests.get("https://track.miem.hse.ru/api/v1/tasks",
                                    headers={'x-disable-pagination': 'true'})
taiga_us_response = requests.get("https://track.miem.hse.ru/api/v1/userstories",
                                 headers={"x-disable-pagination": "true"})
if zulip_response.status_code == jitsi_1response.status_code == jitsi_2response.status_code \
        == git_response.status_code == taiga_us_response.status_code == taiga_tasks_response.status_code == 200:
    # Zulip
    zulip_data = zulip_response.json()
    total_zulip_messages = len(zulip_data["messages"])
    zulip_streams_numbers = []
    zulip_streams_names = []
    for x in zulip_data["messages"]:
        if x["stream_id"] not in zulip_streams_numbers:
            zulip_streams_numbers.append(x["stream_id"])
            zulip_streams_names.append(x["name"])
    zulip_first_data = {}
    for x in zulip_data["stats"]:
        message_count = x["messageCount"]
        if message_count != 0:
            line = x["beginDate"].split()
            current_date = line[1] + " " + line[2]
            zulip_first_data[current_date] = message_count
    fig1 = px.bar(x=zulip_first_data.keys(),
                  y=zulip_first_data.values(),
                  labels={"x": "Дата", "y": "Количество сообщений"},
                  title="Сообщения по дням")
    accumulate = []
    count = 0
    for key in zulip_first_data:
        count += zulip_first_data[key]
        accumulate.append(count)
    fig2 = px.line(x=zulip_first_data.keys(),
                   y=accumulate,
                   title="Линейное изменение общего количества сообщений",
                   markers=True,
                   labels={"x": "Дата", "y": "Общее количество сообщений"})
    # Jitsi

    jitsi_data = jitsi_1response.json()
    jitsi_first_data = {}
    for x in jitsi_data:
        if x["room"] not in jitsi_rooms:
            jitsi_rooms.append(x["room"])
        mas = x["date"].split("-")
        line = mas[2] + " " + mas[1] + " " + mas[0]
        minutes = (int(x["end"][:2]) - int(x["begin"][:2])) * 60 + (int(x["end"][3:5]) - int(x["begin"][3:5]))
        study_hours = minutes / 40
        if line not in jitsi_first_data:
            jitsi_first_data[line] = study_hours
        else:
            jitsi_first_data[line] += study_hours

    jitsi_data = jitsi_2response.json()
    for x in jitsi_data:
        if x["room"] not in jitsi_rooms:
            jitsi_rooms.append(x["room"])
        mas = x["date"].split("-")
        line = mas[2] + " " + mas[1] + " " + mas[0]
        minutes = (int(x["end"][:2]) - int(x["begin"][:2])) * 60 + (int(x["end"][3:5]) - int(x["begin"][3:5]))
        study_hours = minutes / 40
        if line not in jitsi_first_data:
            jitsi_first_data[line] = study_hours
        else:
            jitsi_first_data[line] += study_hours
    fig3 = px.bar(x=jitsi_first_data.keys(),
                  y=jitsi_first_data.values(),
                  labels={"x": "Дата", "y": "Академические часы"},
                  title="Количество академических часов")
    accumulate = []
    total_jitsi_sessions = 0
    for key in jitsi_first_data:
        total_jitsi_sessions += jitsi_first_data[key]
        accumulate.append(total_jitsi_sessions)
    fig4 = px.line(x=jitsi_first_data.keys(),
                   y=accumulate,
                   title="Линейное изменение общего количества академических часов",
                   markers=True,
                   labels={"x": "Неделя", "y": "Общее количество академических часов"})
    # Taiga

    taiga_tasks_data = taiga_tasks_response.json()
    taiga_tasks_massive = []
    for x in taiga_tasks_data:
        if x["owner"] == 923:
            taiga_tasks_massive.append(x)

    taiga_us_data = taiga_us_response.json()
    taiga_us_massive = []
    for x in taiga_us_data:
        if x["owner"] == 923:
            taiga_us_massive.append(x)
    taiga_first_data = {}
    for x in taiga_tasks_massive:
        line = x["created_date"][:10].split("-")
        current_date = line[2] + " " + line[1]
        if current_date not in taiga_first_data:
            taiga_first_data[current_date] = 1
        else:
            taiga_first_data[current_date] += 1
    accum = []
    count = 0
    for x in taiga_first_data:
        count += taiga_first_data[x]
        accum.append(count)
    fig5 = px.line(x=taiga_first_data.keys(),
                   y=accum,
                   labels={"x": "Дата", "y": "Количество задач"},
                   title="Создание задач")
    total_us = len(taiga_us_massive)
    total_tasks = len(taiga_tasks_massive)
    # Git

    git_data = git_response.json()
    git_first_data = {}
    total_commits = 0
    for x in git_data["projects"]:
        total_commits += x["commitCount"]
        for y in x["commits_stats"]:
            if y["commitCount"] != 0:
                line = y["beginDate"].split()
                current_date = line[1] + " " + line[2]
                if current_date not in git_first_data:
                    git_first_data[current_date] = y["commitCount"]
                else:
                    git_first_data[current_date] += y["commitCount"]
    git_first_data = dict(sorted(git_first_data.items(), key=lambda x: x[0]))

    fig6 = px.bar(x=git_first_data.keys(),
                  y=git_first_data.values(),
                  labels={"x": "Дата", "y": "Количество коммитов"},
                  title="Коммиты")
    count = 0
    accum = []
    for x in git_first_data:
        count += git_first_data[x]
        accum.append(count)
    fig7 = px.line(x=git_first_data.keys(),
                   y=accum,
                   labels={"x": "Дата", "y": "Количество коммитов"},
                   title="Коммиты")

    html = open('/home/prsem/rnziyazetdinov/rnziyazetdinov/template.html').read()
    template = Template(html)

    with open('/var/www/html/students/rnziyazetdinov/rnziyazetdinov.html', 'w+') as fh:
        fh.write(template.render(time=datetime.now().isoformat(),
                                 total_messages_zulip=total_zulip_messages,
                                 zulip_streams_names=' / '.join(zulip_streams_names),
                                 first_plot_zulip=fig1.to_html(),
                                 second_plot_zulip=fig2.to_html(),
                                 total_sessions_jitsi=total_jitsi_sessions,
                                 jitsi_rooms=' / '.join(jitsi_rooms),
                                 first_plot_jitsi=fig3.to_html(),
                                 second_plot_jitsi=fig4.to_html(),
                                 total_userstories=total_us,
                                 total_tasks=total_tasks,
                                 plot_taiga=fig5.to_html(),
                                 total_commits=total_commits,
                                 first_plot_gitlab=fig6.to_html(),
                                 second_plot_gitlab=fig7.to_html()))
