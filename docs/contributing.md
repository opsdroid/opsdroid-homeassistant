# Contributing

Contributing to the opsdroid ecosystem is strongly encouraged and every little bit counts!

Check the [issue tracker](https://github.com/opsdroid/opsdroid-homeassistant/issues) for things to work on.

## Testing

The opsdroid-homeassistant test suite relies on [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) to set up a demo instance of Home Assistant to test against.

```console
# Install opsdroid-homeassistant and its dependencies
pip install -e .

# Install the test dependencies including pytest
pip install -r requirements_test.txt

# Run the tests
pytest opsdroid_homeassistant
```

You can also start up the demo Home Assistant yourself and access it via the web interface if you want to have a look at the demo devices when designing your tests.

```console
# Navigate to the tests directory
cd opsdroid_homeassistant/tests

# Start Home Assistant
docker-compose up

# Open http://localhost:8123 in your web browser
# The username and password are both "opsdroid"
```
