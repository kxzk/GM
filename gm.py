#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from datetime import datetime, timedelta
from os import environ
from typing import Dict, Optional

import openai
from github import AuthenticatedUser, Event, Github, NamedUser

openai.api_key = environ["OPENAI_KEY"]


def hey_gpt(events: list[dict]) -> str:
    prompt = f"""
    Hi! Can you write an engineering stand up for me? 
    I'd like it to be a list and include details.
    Here's what I did yesterday:

    {events}
    """

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
    )

    output = completion.choices[0].message["content"].strip()
    return output


GH_EVENTS = [
    #  "CommitCommentEvent",
    #  "CreateEvent",
    #  "DeleteEvent",
    #  "ForkEvent",
    #  "GollumEvent",
    "IssueCommentEvent",
    #  "IssuesEvent",
    #  "MemberEvent",
    #  "PublicEvent",
    "PullRequestEvent",
    "PullRequestReviewEvent",
    "PullRequestReviewCommentEvent",
    "PullRequestReviewThreadEvent",
    "PushEvent",
    #  "ReleaseEvent",
    #  "SponsorshipEvent",
    #  "WatchEvent",
]


def github_user(
    token: str, user: Optional[str] = None
) -> NamedUser.NamedUser | AuthenticatedUser.AuthenticatedUser:
    g = Github(token)
    if user:
        u = g.get_user(user)
    else:
        u = g.get_user()
    return u


def event_dict(event: Event.Event) -> Dict[str, str]:
    E = {}
    E["repo"] = event.repo.full_name
    E["type"] = event.type
    E["created_at"] = event.created_at.date().isoformat()
    return E


def github_event(event: Event.Event) -> Optional[Dict[str, str]]:
    if (
        event.type == "PullRequestReviewEvent"
        and event.payload["review"]["state"] == "approved"
    ):
        E = event_dict(event)
        E["pull_request"] = event.payload["pull_request"]["head"]["ref"]
        E["pull_request_title"] = event.payload["pull_request"]["title"]
        E["review"] = event.payload["review"]["state"]
        return E
    elif event.type == "PushEvent":
        E = event_dict(event)
        E["branch"] = event.payload["ref"]
        E["commit"] = event.payload["commits"][0]["message"]
        return E
    elif event.type == "PullRequestReviewCommentEvent":
        E = event_dict(event)
        E["pull_request"] = event.payload["pull_request"]["head"]["ref"]
        E["pull_request_title"] = event.payload["pull_request"]["title"]
        E["comment"] = event.payload["comment"]["body"]
        E["comment_code"] = event.payload["comment"]["diff_hunk"]
        E["comment_file"] = event.payload["comment"]["path"]
        return E
    elif event.type == "PullRequestEvent" and event.payload["action"] == "opened":
        E = event_dict(event)
        E["pull_request"] = event.payload["pull_request"]["head"]["ref"]
        E["pull_request_title"] = event.payload["pull_request"]["title"]
        E["action"] = event.payload["action"]
        E["body"] = event.payload["pull_request"]["body"]
        return E
    elif event.type == "IssueCommentEvent":
        E = event_dict(event)
        E["issue"] = event.payload["issue"]["title"]
        E["comment"] = event.payload["comment"]["body"]
        return E
    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", type=str, help="GitHub username", required=True)
    parser.add_argument(
        "-o", "--org", type=str, help="GitHub organization", required=True
    )
    parser.add_argument(
        "-t", "--token", type=str, help="GitHub access token", required=True
    )
    parser.add_argument("-d", "--days", type=int, help="Days back", default=1)
    args = parser.parse_args()

    u = github_user(args.token, args.user)

    gh_event_log = []

    for e in u.get_events():
        if (
            e.org is not None
            # belongs to the `--org`
            and e.org.login == args.org
            # events within last `--days`
            and (
                e.created_at.date()
                >= (datetime.today() - timedelta(days=args.days)).date()
            )
            # only certain events
            and e.type in GH_EVENTS
        ):
            E = github_event(e)
            if E is not None:
                gh_event_log.append(E)

    print(hey_gpt(gh_event_log))
