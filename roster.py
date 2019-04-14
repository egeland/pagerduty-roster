#!/usr/bin/env python

# PagerDuty roster - gets all the current on-calls from your schedules, output as JSON
# Copyright (C) 2019  Frode Egeland

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pypd
import datetime
import os
import json

api_token = os.environ.get("PD_API_TOKEN")
schedule_prefix = os.environ.get("PD_SCHEDULE_PREFIX","")

def main():
    try:
        now_oncall = {"schedules": []}
        pypd.api_key = api_token
        schedules = pypd.Schedule.find(query=schedule_prefix)
        for schedule in schedules:
            candidate = get_oncall_person(schedule)
            if len(candidate) > 0:
                now_oncall["schedules"].append(candidate)
        now_oncall["generated"] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc,microsecond=0).isoformat()
        print(json.dumps(now_oncall))
    except pypd.errors.BadRequest as err:
        if err.code == 401:
            print("401 error connecting to PagerDuty - incorrect API token?")
        else:
            print("Error reaching PagerDuty: {}".format(err))
        exit(1)


def get_oncall_person(schedule):
    oncall = {}
    users = schedule.get_oncall(since=datetime.datetime.now(), until=datetime.datetime.now())["users"]
    for user in users:
        if "name" in user:
            u = pypd.User.fetch(id=user["id"], include=["contact_methods"])
            oncall["schedule_name"] = schedule["name"]
            oncall["name"]= u["name"]
            oncall["email"]= u["email"]
            oncall["avatar_url"]= u["avatar_url"]
            for cm in u["contact_methods"]:
                if cm["summary"] == "Mobile":
                    prefix = "0"
                    if cm["country_code"] != 61:
                        prefix = "+{} ".format(cm["country_code"])
                    oncall["mobile"] = "".join([prefix,str(cm["address"])])
                    break
    return oncall

if __name__ == "__main__":
    main()
