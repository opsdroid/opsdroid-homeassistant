# Opsdroid Home Assistant

[![Build Status](https://img.shields.io/travis/com/opsdroid/opsdroid-homeassistant?logo=travis)](https://travis-ci.com/opsdroid/opsdroid-homeassistant)
[![codecov](https://codecov.io/gh/opsdroid/opsdroid-homeassistant/branch/master/graph/badge.svg)](https://codecov.io/gh/opsdroid/opsdroid-homeassistant)
[![Read the Docs](https://img.shields.io/readthedocs/opsdroid-homeassistant)](https://home-assistant.opsdroid.dev/en/latest/)

A plugin for [Opsdroid](https://opsdroid.dev) to enable [Home Assistant](https://home-assistant.io) automation.

Opsdroid is an automation framework for building bots. It is built on an event flow model where events are created (often by a user saying something in a chat client), the events can then be parsed using various AI services to add additional context and finally user defined Python functions called [Skills](https://docs.opsdroid.dev/en/stable/skills/index.html) can be triggered as a result.

Home Assistant is a home control toolkit which allows you to bring all of your smart home devices together into one application. It is also built on an event loop where device states are updated in real time and can trigger automations. Automations in Home Assistant [are defined in YAML](https://www.home-assistant.io/docs/automation/examples/) and can become unwieldy when trying to set up complex automations.

This plugin allows you to bridge the two event loops so that state changes in Home Assistant can trigger Skills in Opsdroid and then Opsdroid can make service calls back to Home Assistant to change states of devices. This enables you to write automations in Python allowing you to define simpler and more readable automations.

```eval_rst
.. toctree::
   :maxdepth: 2

   getting-started
   examples
   helpers
   api
   alternatives
   contributing
```
