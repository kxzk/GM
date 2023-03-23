#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def pytest_addoption(parser):
    parser.addoption(
        "--token",
        action="store",
        help="GitHub access token",
    )
